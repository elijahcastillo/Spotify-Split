if (!localStorage.hasOwnProperty("trackIdx")) {
  localStorage.setItem("trackIdx", 0);
}

//Track Elements
const album_art = document.getElementById("album_art");
const track_title = document.getElementById("track_title");
const track_artist = document.getElementById("track_artist");
const album_name = document.getElementById("album_name");
const release_date = document.getElementById("release_date");
const track_duration = document.getElementById("track_duration");
const mp3_src = document.getElementById("mp3_src");
const audio = document.getElementById("audio");

//Loading
const spin = document.getElementById("spin");
spin.visibility = "hidden";
const trackData = document.getElementById("tr");

//Control Buttons
const nextBtn = document.getElementById("next");
const backBtn = document.getElementById("back");
const nextAction = document.getElementById("nextAction");
const backAction = document.getElementById("backAction");
const actionForm = document.getElementById("actionForm");

//global track array
class Tracks {
  constructor() {
    this.tracks = [];
    this.offset = 0;
    this.BATCH_SIZE = 20;
  }

  setTracks(tracks) {
    this.tracks = tracks;
  }

  setOffset(offset) {
    this.offset = offset;
  }

  getCurrentIdx() {
    return parseInt(localStorage.getItem("trackIdx"));
  }

  getCurrentURI() {
    const current_track = this.tracks[this.getCurrentIdx() - this.offset];
    const URI = current_track.track_uri;
    return URI;
  }

  render() {
    // console.log("\n ");
    // console.log(this.tracks, "RENDER TRACKS");
    const current_track = this.tracks[this.getCurrentIdx() - this.offset];
    // console.log(this.getCurrentIdx() - this.offset, "INDEX FOR RENDER");
    // console.log(current_track, "RENDER TRACK");
    // console.log(this.offset, "RENDER OFFSET");

    const year = current_track.release_date.substring(0, 4);
    const length = msToTime(current_track.duration);

    //Change displayed track data
    album_art.src = current_track.album_url;
    track_title.textContent = current_track.title;
    track_artist.textContent = current_track.artist;
    album_name.textContent = current_track.album_name;
    release_date.textContent = year;
    track_duration.textContent = length;
    mp3_src.src = current_track.mp3_url;

    //Needed if changing src dynamically
    audio.load();
  }

  nextTrack() {
    let currentIdx = this.getCurrentIdx();

    //Check if there are no more tracks
    if (
      this.tracks.length < this.BATCH_SIZE &&
      currentIdx - this.offset == this.tracks.length - 1
    ) {
      return sendToast(0, "No more tracks in playlist");
    }
    localStorage.setItem("trackIdx", currentIdx + 1);
  }

  previousTrack() {
    let currentIdx = this.getCurrentIdx();

    //Cant have a negitive idx
    if (currentIdx == 0) {
      return;
    }
    localStorage.setItem("trackIdx", currentIdx - 1);
  }

  //Get next batch of tracks
  async nextBatch() {
    let currentIdx = this.getCurrentIdx();

    if (currentIdx % this.BATCH_SIZE == 0) {
      console.log("--------------------- Refetch Next ---------------------");
      this.offset += this.BATCH_SIZE;
      this.setTracks(await getTrackData(this.offset));
    }
  }

  //Get previous batch of tracks
  async previousBatch() {
    let currentIdx = this.getCurrentIdx();

    if (currentIdx % this.BATCH_SIZE == 19) {
      console.log("--------------------- Refetch Prev ---------------------");
      this.offset -= 20;
      this.setTracks(await getTrackData(this.offset));
    }
  }
}
const Track = new Tracks();

function sendToast(type, message, remove = true) {
  // 0 - BAD   1 - GOOD
  console.log("HHHH");
  const toast = document.getElementById("toast");

  toast.textContent = message;
  if (type) {
    toast.style.backgroundColor = "green";
  } else {
    toast.style.backgroundColor = "red";
  }

  toast.classList.add("toast_active");

  if (remove) {
    setTimeout(() => {
      toast.classList.remove("toast_active");
    }, 3000);
  }
}

function msToTime(duration) {
  var seconds = Math.floor((duration / 1000) % 60),
    minutes = Math.floor((duration / (1000 * 60)) % 60),
    minutes = minutes < 10 ? "0" + minutes : minutes;
  seconds = seconds < 10 ? "0" + seconds : seconds;

  return minutes + ":" + seconds;
}

async function getTrackData(offset = 0) {
  spin.style.visibility = "visible";
  trackData.style.visibility = "hidden";
  const res = await fetch("get-tracks", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      offset: offset,
    }),
  });

  const data = await res.json();

  spin.style.visibility = "hidden";
  trackData.style.visibility = "visible";

  return data;
}

async function main() {
  //get offset that current track idx would be in
  let initOffset = Math.floor(Track.getCurrentIdx() / 10) * 10;

  //Get Inital Tracks
  const data = await getTrackData(initOffset);
  console.log("INIT FETCH: ", data);
  Track.setTracks(data);
  Track.setOffset(initOffset);
  Track.render();
}

//Wrapper Function to disable button while running a function
function disable(func, ele) {
  return async function () {
    ele.disabled = true;
    await func();
    unSelectPlaylist();
    ele.disabled = false;
  };
}

//Get next track in playlist
async function next() {
  Track.nextTrack();
  await Track.nextBatch();
  Track.render();
}

//Get previous track in playlist
async function previous() {
  Track.previousTrack();
  await Track.previousBatch();
  Track.render();
}

function sendAction(endpoint, msg) {
  const childIds = getSelectedChildren();
  const trackURI = Track.getCurrentURI();
  const position = Track.getCurrentIdx();
  console.log(endpoint, childIds.length);

  //No selected playlist for needed actions
  if (
    (endpoint == "add" || endpoint == "add-and-delete") &&
    childIds.length == 0
  ) {
    return sendToast(0, "Please select a Playlist(s)");
  }

  sendToast(0, "Sending Request", false);

  fetch(endpoint, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      child_ids: childIds,
      uri: trackURI,
      position: position,
    }),
  })
    .then(() => sendToast(1, msg))
    .catch((err) => {
      console.log("ACTION ERR: ", err);
      sendToast(0, "Action Error");
    });
}

function checkAndDispatch(action) {
  switch (action) {
    case "Track Added":
      sendAction("add", action);
      break;

    case "Added & Deleted":
      sendAction("add-and-delete", action);
      break;

    case "Deleted":
      sendAction("delete_from_root", action);
      break;
  }
}

//Unselect all children playlist
function unSelectPlaylist() {
  var checkboxes = actionForm.querySelectorAll(".child");
  Array.from(checkboxes).forEach((el) => {
    if (el.checked) {
      el.checked = false;
    }
  });
}

function getSelectedChildren() {
  var checkboxes = actionForm.querySelectorAll(".child");

  //checks if input is checked and removes undefined vales from map func
  const childrenPlaylistIds = Array.from(checkboxes)
    .map((element) => {
      if (element.checked) return element.value;
    })
    .filter((item) => item);

  return childrenPlaylistIds;
}

nextBtn.addEventListener("click", async (e) => {
  const wrapped = disable(next, e.target);
  await wrapped();
});

backBtn.addEventListener("click", async (e) => {
  const wrapped = disable(previous, e.target);
  await wrapped();
});

nextAction.addEventListener("click", async (e) => {
  //Get radio btn value from form
  const checked = actionForm.querySelector("input[name=action]:checked");
  checkAndDispatch(checked.value);

  const wrapped = disable(next, e.target);
  await wrapped();
});

backAction.addEventListener("click", async (e) => {
  //Get radio btn value from form
  const checked = actionForm.querySelector("input[name=action]:checked");
  checkAndDispatch(checked.value);

  const wrapped = disable(previous, e.target);
  await wrapped();
});

main();

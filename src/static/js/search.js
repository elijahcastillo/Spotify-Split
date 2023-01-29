console.log(playlists);

const input = document.getElementById("search");

function filterPlaylists() {
  const value = input.value.toLowerCase();
  playlists.forEach((playlist) => {
    const item = document.getElementById(`${playlist.id}`);
    if (playlist.name.toLowerCase().includes(value)) {
      item.style.display = "flex";
    } else {
      item.style.display = "none";
    }
  });
}

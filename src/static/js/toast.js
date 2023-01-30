function sendToast(type, message, remove = true) {
  // 0 - BAD   1 - GOOD

  const toast = document.getElementById("toast");

  toast.textContent = message;
  toast.style.color = "white";
  if (type == 1) {
    toast.style.backgroundColor = "green";
  } else if (type == 2) {
    toast.style.backgroundColor = "yellow";
    toast.style.color = "black";
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

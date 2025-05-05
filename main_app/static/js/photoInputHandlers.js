export function initPhotoInputHandlers() {
  const fileInput = document.getElementById("id_photo");
  const clearCheckbox = document.querySelector("#photo-clear_id");

  if (fileInput && clearCheckbox) {
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length > 0) {
        clearCheckbox.checked = false;
      }
    });
  }
}

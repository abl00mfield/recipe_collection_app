export function initPhotoInputHandlers() {
  // Look for all file inputs on the page
  const fileInputs = document.querySelectorAll('input[type="file"]');

  fileInputs.forEach((fileInput) => {
    const fieldName = fileInput.name; // e.g., "photo" or "profile_picture"
    const clearCheckbox = document.querySelector(`#${fieldName}-clear_id`);

    if (clearCheckbox) {
      fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
          clearCheckbox.checked = false;
        }
      });
    }
  });
}

export function initDropdownHandlers() {
  // Get all dropdown toggle buttons
  const toggleButtons = document.querySelectorAll(".add-icon");

  toggleButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.stopPropagation(); // Prevent this click from being caught by the "outside" listener

      const recipeId = this.dataset.recipe;
      const dropdownToToggle = document.getElementById(`dropdown-${recipeId}`);

      // Close all dropdowns
      document.querySelectorAll(".collection-dropdown").forEach((dropdown) => {
        if (dropdown !== dropdownToToggle) {
          dropdown.classList.add("hidden");
        }
      });

      // Toggle the clicked dropdown
      dropdownToToggle.classList.toggle("hidden");
    });
  });

  // Click outside to close all dropdowns
  document.addEventListener("click", function (e) {
    const isDropdown = e.target.closest(".collection-dropdown");
    const isButton = e.target.closest(".add-icon");

    if (!isDropdown && !isButton) {
      document.querySelectorAll(".collection-dropdown").forEach((dropdown) => {
        dropdown.classList.add("hidden");
      });
    }
  });
}

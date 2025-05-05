export function initDropdownHandlers() {
  //hidden menu for collection dropdown
  document.querySelectorAll(".add-icon").forEach((button) => {
    button.addEventListener("click", function () {
      const recipeId = this.dataset.recipe;
      const dropdown = document.getElementById(`dropdown-${recipeId}`);
      dropdown.classList.toggle("hidden");
    });
  });

  //hides the dropdown menu if a user clicks outside of it
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".collection-dropdown").forEach((dropdown) => {
      const isDropdown = dropdown.contains(e.target);
      const isButton = e.target.closest(".add-icon");
      if (!isDropdown && !isButton) {
        dropdown.classList.add("hidden");
      }
    });
  });
}

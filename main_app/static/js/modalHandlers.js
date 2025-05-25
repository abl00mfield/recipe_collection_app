export function initModalHandlers() {
  //adding a new collection if a user wants to create a collection on the fly

  const selects = document.querySelectorAll(".collection-select");
  const modal = document.getElementById("new-collection-modal");
  const recipeInput = document.getElementById("new-collection-recipe-id");
  const cancelBtn = document.getElementById("cancel-modal");

  const newCollectionButtons = document.querySelectorAll(".new-collection-btn");

  selects.forEach((select) => {
    select.addEventListener("change", function () {
      if (select.value === "__new__") {
        modal.classList.remove("hidden");
        recipeInput.value = select.dataset.recipeId;
        select.selectedIndex = 0;
      } else {
        select.closest("form").submit();
      }
    });
  });

  newCollectionButtons.forEach((button) => {
    button.addEventListener("click", function () {
      //get recipeID from dropdown's id
      const dropdown = button.closest(".collection-dropdown");
      if (dropdown && dropdown.id.startsWith("dropdown-")) {
        const recipeId = dropdown.id.split("-")[1];
        recipeInput.value = recipeId;
        modal.classList.remove("hidden");
      }
    });
  });

  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
      recipeInput.value = "";
    });
  }
}

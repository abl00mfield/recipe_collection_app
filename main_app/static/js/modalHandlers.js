export function initModalHandlers() {
  //adding a new collection if a user wants to create a collection on the fly

  const selects = document.querySelectorAll(".collection-select");
  const modal = document.getElementById("new-collection-modal");
  const recipeInput = document.getElementById("new-collection-recipe-id");
  const cancelBtn = document.getElementById("cancel-modal");

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

  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
      recipeInput.value = "";
    });
  }
}

import { showToast } from "./toast.js";

export function initCollectionAddHandlers() {
  document.querySelectorAll(".add-to-collection-form").forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const url = this.action;
      const formData = new FormData(this);

      const urlParts = this.action.split("/").filter(Boolean); // removes empty strings
      const recipeId = urlParts[urlParts.length - 2]; // gets the number before 'add_to_collection'

      const isDropdownForm = this.closest(".collection-dropdown") !== null;

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
          },
          body: formData,
        });

        if (!response.ok) throw new Error("Request failed");

        //CASE A - adding from target collection
        if (!isDropdownForm) {
          const icon = this.querySelector("button i");
          if (icon) {
            icon.classList.remove("fa-plus");
            icon.classList.add("fa-check");
            icon.title = "Already in Collection";
          }
          const btn = this.querySelector("button");
          if (btn) btn.disabled = true;
          // case B - bookmark dropdown form
        } else {
          //disable specific dropdown item
          const dropdownItem = this.closest("li");
          if (dropdownItem) {
            dropdownItem.innerHTML = `${dropdownItem.textContent.trim()} ☑️`;
            dropdownItem.classList.add("disabled");
          }

          // updated the bookmark to solid if not already
          const bookmarkIcon = document.querySelector(
            `.add-icon[data-recipe="${recipeId}"] i`
          );
          console.log("recipeId", recipeId);
          console.log("bookmarkIcon: ", bookmarkIcon);
          if (bookmarkIcon && bookmarkIcon.classList.contains("fa-regular")) {
            bookmarkIcon.classList.remove("fa-regular");
            bookmarkIcon.classList.add("fa-solid");
          }
        }
        const recipeTitle = JSON.parse(`"${this.dataset.recipeTitle}"`);
        const collectionName = JSON.parse(`"${this.dataset.collectionName}"`);
        if (recipeTitle && collectionName) {
          showToast(
            `"${recipeTitle}" was added to "${collectionName}"`,
            "success"
          );
        } else {
          showToast("Recipe aded to collection!", "success");
        }
      } catch (err) {
        console.error("Error: ", err);
      }
    });
  });
}

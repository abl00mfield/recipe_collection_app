import { showToast } from "./toast.js";

export function initCollectionAddHandlers(targetForm = null) {
  const forms = targetForm
    ? [targetForm]
    : document.querySelectorAll(".add-to-collection-form");

  forms.forEach((form) => {
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
          //toggle specific dropdown item
          const dropdownItem = this.closest("li");
          if (dropdownItem) {
            const recipeTitle = this.dataset.recipeTitle;
            const collectionName = this.dataset.collectionName;
            const nextUrl = formData.get("next");
            const collectionId = formData.get("collection_id");
            dropdownItem.innerHTML = ` <form method="POST"
                        action="/collections/${collectionId}/remove/${recipeId}"
                        class="remove-from-collection-form no-spinner"
                        data-recipe-title="${recipeTitle}"
                        data-collection-name="${collectionName}"
                        data-recipe="${recipeId}">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${formData.get(
                      "csrfmiddlewaretoken"
                    )}">
                    <input type="hidden" name="next" value="${nextUrl}">
                    <button type="submit" class="collection-item">
                    ${collectionName} ☑️ (click to remove)
                    </button>
                </form>`;

            const newRemoveForm = dropdownItem.querySelector(
              ".remove-from-collection-form"
            );
            if (newRemoveForm) {
              initCollectionRemoveHandlers(newRemoveForm);
            }
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
          showToast("Recipe added to collection!", "success");
        }
      } catch (err) {
        console.error("Error: ", err);
      }
    });
  });
}

export function initCollectionRemoveHandlers(targetForm = null) {
  const forms = targetForm
    ? [targetForm]
    : document.querySelectorAll(".remove-from-colleciton-form");

  forms.forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const url = this.action;
      const formData = new FormData(this);
      const recipeId = this.dataset.recipe;

      const overlay = document.getElementById("loading-overlay");
      let showSpinnerTimeout = setTimeout(() => {
        overlay?.classList.remove("hidden");
      }, 150);

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
          },
          body: formData,
        });

        if (!response.ok) throw new Error("Failed to remove");

        //replace the dropdown item with an active add buttons
        const li = this.closest("li");
        if (li) {
          const collectionName = this.dataset.collectionName;
          const collectionId = this.action.split("/")[4];
          li.innerHTML = `
            <form method="POST"
                action="/recipes/${recipeId}/add-to-collection/"
                class="add-to-collection-form no-spinner"
                data-recipe-title="${this.dataset.recipeTitle}"
                data-collection-name="${collectionName}"
                data-recipe="${recipeId}">
                <input type="hidden" name="collection_id" value="${collectionId}">
                <input type="hidden" name="next" value="${formData.get(
                  "next"
                )}">
                <input type="hidden" name="csrfmiddlewaretoken" value="${formData.get(
                  "csrfmiddlewaretoken"
                )}">
                <button type="submit" class="collection-item">${collectionName}</button>
            </form>`;

          // 🔁 Re-initialize the new add form
          const newAddForm = li.querySelector(".add-to-collection-form");
          if (newAddForm) {
            initCollectionAddHandlers(newAddForm); // 💡 pass form directly
          }
        }
        //TODO revert bookmark icon if needed

        //toast
        const recipeTitle = JSON.parse(`"${this.dataset.recipeTitle}"`);
        const collectionName = JSON.parse(`"${this.dataset.collectionName}"`);
        showToast(
          `"${recipeTitle}" removed from "${collectionName}"`,
          "success"
        );
      } catch (err) {
        console.error(err);
        showToast("Could not remove recipe", "error");
      } finally {
        clearTimeout(showSpinnerTimeout);
        overlay?.classList.add("hidden");
      }
    });
  });
}

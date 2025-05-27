import { showToast } from "./toast.js";

function createCollectionForm({
  mode, // "add" or "remove"
  recipeId,
  collectionId,
  recipeTitle,
  collectionName,
  csrfToken,
  nextUrl,
}) {
  const form = document.createElement("form");
  form.method = "POST";
  form.className = `${mode}-from-collection-form no-spinner`;
  form.dataset.recipe = recipeId;
  form.dataset.recipeTitle = recipeTitle;
  form.dataset.collectionName = collectionName;
  form.action =
    mode === "add"
      ? `/recipes/${recipeId}/add-to-collection/`
      : `/collections/${collectionId}/remove/${recipeId}`;

  form.innerHTML = `
    <input type="hidden" name="collection_id" value="${collectionId}">
    <input type="hidden" name="next" value="${nextUrl}">
    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
    <button type="submit" class="collection-item">
      ${
        mode === "add"
          ? collectionName
          : `${collectionName} ☑️ (click to remove)`
      }
    </button>
  `;

  return form;
}

export function initCollectionAddHandlers(targetForm = null) {
  const forms = targetForm
    ? [targetForm]
    : document.querySelectorAll(".add-to-collection-form");

  forms.forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const url = this.action;
      const formData = new FormData(this);
      const collectionId = formData.get("collection_id");
      const recipeId = this.dataset.recipe;
      const recipeTitle = JSON.parse(`"${this.dataset.recipeTitle}"`);
      const collectionName = JSON.parse(`"${this.dataset.collectionName}"`);
      const nextUrl = formData.get("next");
      const isDropdownForm = this.closest(".collection-dropdown") !== null;

      const urlParts = this.action.split("/").filter(Boolean); // removes empty strings
      //   const recipeId = urlParts[urlParts.length - 2]; // gets the number before 'add_to_collection'

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
          const newRemoveForm = createCollectionForm({
            mode: "remove",
            recipeId,
            collectionId,
            recipeTitle: this.dataset.recipeTitle,
            collectionName: this.dataset.collectionName,
            csrfToken: formData.get("csrfmiddlewaretoken"),
            nextUrl,
          });
          this.replaceWith(newRemoveForm);
          initCollectionRemoveHandlers(newRemoveForm);
        }

        // updated the bookmark to solid if not already
        const bookmarkIcon = document.querySelector(
          `.add-icon[data-recipe="${recipeId}"] i`
        );

        if (bookmarkIcon && bookmarkIcon.classList.contains("fa-regular")) {
          bookmarkIcon.classList.remove("fa-regular");
          bookmarkIcon.classList.add("fa-solid");
        }

        if (recipeTitle && collectionName) {
          showToast(
            `"${recipeTitle}" was added to "${collectionName}"`,
            "success"
          );
        } else {
          showToast("Recipe added to collection!", "success");
        }
      } catch (err) {
        console.error("Could not add recipe: ", err);
      }
    });
  });
}

export function initCollectionRemoveHandlers(targetForm = null) {
  const forms = targetForm
    ? [targetForm]
    : document.querySelectorAll(".remove-from-collection-form");

  forms.forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const url = this.action;
      const formData = new FormData(this);
      const recipeId = this.dataset.recipe;
      const recipeTitle = JSON.parse(`"${this.dataset.recipeTitle}"`);
      const collectionName = JSON.parse(`"${this.dataset.collectionName}"`);
      const collectionId = this.action.split("/")[4];

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
        const newAddForm = createCollectionForm({
          mode: "add",
          recipeId,
          collectionId,
          recipeTitle: this.dataset.recipeTitle,
          collectionName: this.dataset.collectionName,
          csrfToken: formData.get("csrfmiddlewaretoken"),
          nextUrl: formData.get("next"),
        });
        this.replaceWith(newAddForm);
        initCollectionAddHandlers(newAddForm);

        //revert bookmark icon if needed
        const dropdown = document.querySelector(`#dropdown-${recipeId}`);
        const stillSaved = dropdown?.querySelector(
          ".remove-from-collection-form"
        );

        if (!stillSaved) {
          const bookmarkIcon = document.querySelector(
            `.add-icon[data-recipe="${recipeId}"] i`
          );
          if (bookmarkIcon && bookmarkIcon.classList.contains("fa-solid")) {
            bookmarkIcon.classList.remove("fa-solid");
            bookmarkIcon.classList.add("fa-regular");
          }
        }

        //toast

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

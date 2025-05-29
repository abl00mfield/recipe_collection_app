import {
  initCollectionAddHandlers,
  initCollectionRemoveHandlers,
  createCollectionForm,
} from "./recipe-list.js";
import { showToast } from "./toast.js";

function insertListItemAlphabetically(listElement, newLi, newCollectionName) {
  const existingItems = Array.from(listElement.querySelectorAll("li"));
  const newName = newCollectionName.toLowerCase();

  for (let i = 0; i < existingItems.length; i++) {
    const button = existingItems[i].querySelector("button.collection-item");
    if (!button || button.classList.contains("new-collection-btn")) continue;

    const itemName = button.textContent
      .replace("☑️ (click to remove)", "")
      .trim()
      .toLowerCase();

    if (newName < itemName) {
      listElement.insertBefore(newLi, existingItems[i]);
      return;
    }
  }

  // If no earlier item found, insert before the new collection button or at end
  const newButtonLi = listElement
    .querySelector("button.new-collection-btn")
    ?.closest("li");
  if (newButtonLi) {
    listElement.insertBefore(newLi, newButtonLi);
  } else {
    listElement.appendChild(newLi);
  }
}

export function initModalHandlers() {
  //adding a new collection if a user wants to create a collection on the fly
  //TODO:  check if user is not in any collections and update bookmark if so

  const selects = document.querySelectorAll(".collection-select");
  const modal = document.getElementById("new-collection-modal");
  const recipeInput = document.getElementById("new-collection-recipe-id");
  const cancelBtn = document.getElementById("cancel-modal");
  const newCollectionButtons = document.querySelectorAll(".new-collection-btn");
  const newCollectionForm = document.querySelector(".new-collection-form");

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
      const recipeTitle = button
        .closest(".recipe-card")
        .querySelector("h4").innerText;

      if (dropdown && dropdown.id.startsWith("dropdown-")) {
        const recipeId = dropdown.id.split("-")[1];
        recipeInput.value = recipeId;
        modal.classList.remove("hidden");
      }
    });
  });

  if (newCollectionForm) {
    newCollectionForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const url = this.action;
      const formData = new FormData(this);
      const collectionName = formData.get("name").trim();
      const recipeId = recipeInput.value;
      const dropdown = document.querySelector(`#dropdown-${recipeId}`);
      const recipeTitle = dropdown
        .closest(".recipe-card")
        .querySelector("h4").innerText;

      const collections = dropdown.querySelectorAll(".collection-item");
      const collectionsClean = Array.from(collections).map((collection) =>
        collection.textContent
          .replace("☑️ (click to remove)", "")
          .trim()
          .toLowerCase()
      );

      if (collectionsClean.includes(collectionName.toLowerCase())) {
        showToast("Collection already exists", "error");
        newCollectionForm.reset();
        return;
      }

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
            "X-Requested-with": "XMLHttpRequest",
          },
          body: formData,
        });

        if (!response.ok) throw new Error("Failed to add collection");

        const json = await response.json();
        modal.classList.add("hidden");
        showToast(
          `"${json.collectionName}" collection was created and "${recipeTitle}" was added!`
        );
        newCollectionForm.reset();
        recipeInput.value = "";

        // If this was the first collection, switch the bookmark to solid

        // ✅ Add to current recipe dropdown
        const updatedCollectionItem = createCollectionForm({
          mode: "remove",
          displayMode: "dropdown",
          recipeId: json.recipeId,
          collectionId: json.collectionId,
          recipeTitle,
          collectionName: json.collectionName,
          csrfToken: formData.get("csrfmiddlewaretoken"),
          nextUrl: window.location.href,
        });

        const newListItem = document.createElement("li");
        newListItem.appendChild(updatedCollectionItem);

        const list = dropdown.querySelector(".collection-list");
        insertListItemAlphabetically(list, newListItem, json.collectionName);
        initCollectionRemoveHandlers(updatedCollectionItem);

        const otherForms = dropdown.querySelectorAll(
          ".remove-from-collection-form"
        );
        if (otherForms.length === 1) {
          const bookmarkIcon = dropdown
            .closest(".recipe-card")
            .querySelector(".add-icon i");

          if (bookmarkIcon?.classList.contains("fa-regular")) {
            bookmarkIcon.classList.remove("fa-regular");
            bookmarkIcon.classList.add("fa-solid");
          }
        }

        // Add to all other dropdowns
        document
          .querySelectorAll(".collection-dropdown")
          .forEach((otherDropdown) => {
            const otherRecipeId = otherDropdown.id.split("-")[1];
            if (otherRecipeId === json.recipeId) return;

            const titleElement = otherDropdown
              .closest(".recipe-card")
              ?.querySelector("h4");
            const otherRecipeTitle = titleElement ? titleElement.innerText : "";

            const addForm = createCollectionForm({
              mode: "add",
              displayMode: "dropdown",
              recipeId: otherRecipeId,
              collectionId: json.collectionId,
              recipeTitle: otherRecipeTitle,
              collectionName: json.collectionName,
              csrfToken: formData.get("csrfmiddlewaretoken"),
              nextUrl: window.location.href,
            });

            const li = document.createElement("li");
            li.appendChild(addForm);

            const otherList = otherDropdown.querySelector(".collection-list");
            insertListItemAlphabetically(otherList, li, json.collectionName);
            initCollectionAddHandlers(addForm);
          });
      } catch (err) {
        console.error("Collection not created: ", err.message);
        showToast("Failed to create collection", "error");
      }
    });
  }

  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
      recipeInput.value = "";
    });
  }
}

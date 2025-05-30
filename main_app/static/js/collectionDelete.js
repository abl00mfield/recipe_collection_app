import { showToast } from "./toast.js";

export function initCollectionDelete() {
  const page = document.getElementById("collection-list-page");

  //only run this code on the collection list page
  if (!page) return;
  const deleteForms = document.querySelectorAll(".delete-form");

  deleteForms.forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const url = this.action;
      const formData = new FormData(this);
      const collectionCard = this.closest(".collection-card");
      const collectionName = formData.get("collection-name");

      if (!confirm(`Are you sure you want to delete "${collectionName}"?`)) {
        return;
      }

      const overlay = document.getElementById("loading-overlay");
      overlay.classList.remove("hidden");

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
          },
          body: formData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || "Request failed");
        }

        if (collectionCard) {
          collectionCard.remove();
        }
        const remainingCards = document.querySelectorAll(".collection-card");
        if (remainingCards.length === 0) {
          const container = document.querySelector(".collection-list");
          container.innerHTML = `
            <div class="no-collections">
              <p>No collections yet. Add one now!</p>
              <a class="btn" href="/collections/create/">Add a New Collection</a>
            </div>`;
        }
        showToast(`Collection ${collectionName} was deleted!`);
      } catch (err) {
        console.error("Collection not deleted", err.message);
      } finally {
        overlay.classList.add("hidden");
      }
    });
  });
}

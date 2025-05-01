document.addEventListener("DOMContentLoaded", function () {
  const messages = document.querySelectorAll(".messages li");

  messages.forEach((message) => {
    setTimeout(() => {
      message.classList.add("fade-out"); // Add the class for sliding + fading
      setTimeout(() => {
        message.remove();
      }, 1000); // wait for fade/slide animation to complete
    }, 3000); // start fade/slide after 3 seconds
  });

  // Convert UTC <time> elements to user's local time
  const elements = document.querySelectorAll("time.utc-timestamp");
  elements.forEach((el) => {
    const utcTime = new Date(el.getAttribute("datetime"));
    const localString = utcTime.toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
    el.textContent = localString;
  });

  //adds a spinner overlay for loading
  const form = document.querySelector("form");
  const overlay = document.getElementById("loading-overlay");

  if (form && overlay) {
    form.addEventListener("submit", () => {
      const message =
        form.dataset.loadingMessage || "Submitting, please wait...";
      overlay.querySelector("p").textContent = message;
      overlay.classList.remove("hidden");
    });
  }

  //adding a new collection if user wants to create collection on the fly
  const selects = document.querySelectorAll(".collection-select");
  const modal = document.getElementById("new-collection-modal");
  const recipeInput = document.getElementById("new-collection-recipe-id");
  const cancelBtn = document.getElementById("cancel-modal");

  selects.forEach((select) => {
    select.addEventListener("change", function () {
      if (select.value === "__new__") {
        modal.classList.remove("hidden");
        recipeInput.value = select.dataset.recipeId;
        // Reset the select so it doesn't stay on "+ New Collection"
        select.selectedIndex = 0;
      }
    });
  });

  cancelBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
    recipeInput.value = "";
  });

  //hidden menu for collection icon

  document.querySelectorAll(".add-icon").forEach((button) => {
    button.addEventListener("click", function () {
      const recipeId = this.dataset.recipe;
      const dropdown = document.getElementById(`dropdown-${recipeId}`);
      dropdown.classList.toggle("hidden");
    });
  });

  document.querySelectorAll(".recipe-card").forEach((card) => {
    card.addEventListener("click", function (e) {
      // Don’t follow if clicking a form element inside
      if (
        !e.target.closest("form") &&
        !e.target.closest(".collection-dropdown-wrapper")
      ) {
        window.location.href = card.dataset.href;
      }
    });
  });
});

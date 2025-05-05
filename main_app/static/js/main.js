document.addEventListener("DOMContentLoaded", function () {
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
      } else {
        select.closest("form").submit();
      }
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

  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      modal.classList.add("hidden");
      recipeInput.value = "";
    });
  }
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

  document.querySelectorAll(".collection-card").forEach((card) => {
    card.addEventListener("click", function (e) {
      if (!e.target.closest("form")) {
        window.location.href = card.dataset.href;
      }
    });
  });

  const fileInput = document.getElementById("id_photo");
  const clearCheckbox = document.querySelector("#photo-clear_id");

  //if user checks the box to clear the file and upload a new file
  if (fileInput && clearCheckbox) {
    fileInput.addEventListener("change", () => {
      if (fileInput.files.length > 0) {
        clearCheckbox.checked = false;
      }
    });
  }

  const hamburger = document.getElementById("hamburger");
  const navLinks = document.getElementById("nav-links");

  hamburger.addEventListener("click", () => {
    navLinks.classList.toggle("show-nav");
  });
});

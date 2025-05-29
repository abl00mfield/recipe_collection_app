//adds a spinner overlay for loading

export function initFormSpinner() {
  const form = document.querySelector("form:not(.no-spinner)");
  const overlay = document.getElementById("loading-overlay");

  if (!overlay) return;

  if (form && overlay) {
    form.addEventListener("submit", () => {
      const message =
        form.dataset.loadingMessage || "Submitting, please wait...";
      overlay.querySelector("p").textContent = message;
      overlay.classList.remove("hidden");
    });
  }
}

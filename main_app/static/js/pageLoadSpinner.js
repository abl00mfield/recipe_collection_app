// static/js/pageLoadSpinner.js

export function initPageLoadSpinner() {
  const overlay = document.getElementById("loading-overlay");
  if (!overlay) return;

  // Show spinner on <a> clicks that load a new page
  document.body.addEventListener("click", (e) => {
    const link = e.target.closest("a");
    if (
      link &&
      link.getAttribute("href") &&
      !link.getAttribute("target") &&
      !link.getAttribute("href").startsWith("#") &&
      !link.classList.contains("no-spinner")
    ) {
      overlay.querySelector("p").textContent = "Loading recipes...";
      overlay.classList.remove("hidden");
    }
  });

  // Show spinner on form submissions (like filter/search)
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    form.addEventListener("submit", () => {
      const message = form.dataset.loadingMessage || "Loading, please wait...";
      overlay.querySelector("p").textContent = message;
      overlay.classList.remove("hidden");
    });
  });
}

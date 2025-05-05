export function initCardNavigation() {
  //making the entire card clickable if there is a form element on the card

  document.querySelectorAll(".recipe-card").forEach((card) => {
    card.addEventListener("click", function (e) {
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
}

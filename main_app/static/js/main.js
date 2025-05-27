import { initLocalTimestamps } from "./initLocalTimestamps.js";
import { initFormSpinner } from "./formSpinner.js";
import { initDropdownHandlers } from "./dropdownHandlers.js";
import { initModalHandlers } from "./modalHandlers.js";
import { initCardNavigation } from "./cardNavigation.js";
import { initPhotoInputHandlers } from "./photoInputHandlers.js";
import { initMobileNav } from "./mobileNav.js";
import { initPageLoadSpinner } from "./pageLoadSpinner.js";
import { initCollectionAddHandlers } from "./recipe-list.js";
import { initCollectionRemoveHandlers } from "./recipe-list.js";

document.addEventListener("DOMContentLoaded", () => {
  initLocalTimestamps();
  initFormSpinner();
  initDropdownHandlers();
  initModalHandlers();
  initCardNavigation();
  initPhotoInputHandlers();
  initMobileNav();
  initPageLoadSpinner();
  initCollectionAddHandlers();
  initCollectionRemoveHandlers();
  window.addEventListener("pageshow", () => {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
      overlay.classList.add("hidden");
    }
  });
});

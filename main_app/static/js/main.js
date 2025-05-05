import { initLocalTimestamps } from "./initLocalTimestamps.js";
import { initFormSpinner } from "./formSpinner.js";
import { initDropdownHandlers } from "./dropdownHandlers.js";
import { initModalHandlers } from "./modalHandlers.js";
import { initCardNavigation } from "./cardNavigation.js";
import { initPhotoInputHandlers } from "./photoInputHandlers.js";
import { initMobileNav } from "./mobileNav.js";

document.addEventListener("DOMContentLoaded", () => {
  initLocalTimestamps();
  initFormSpinner();
  initDropdownHandlers();
  initModalHandlers();
  initCardNavigation();
  initPhotoInputHandlers();
  initMobileNav();
});

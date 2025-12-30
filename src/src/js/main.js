import Alpine from "alpinejs";
import { countdown } from "./countdown.js";
import { priceRange } from "./priceRange.js";
import "./swiper-script.js";
import "./script.js";

window.Alpine = Alpine;

// register Alpine component globally (optional)
Alpine.data("countdown", (targetDate) => countdown(targetDate));
Alpine.data("priceRange", () => priceRange());

Alpine.start();

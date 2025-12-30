function formatFaNumber(num) {
  return new Intl.NumberFormat("fa-IR").format(num);
}

document.querySelectorAll(".fa-number").forEach((el) => {
  const rawNumber = el.innerText.trim();
  el.innerText = formatFaNumber(rawNumber);
});

const userMenu = document.querySelector(".user-menu");
const openUserMenu = document.querySelector(".open-user-menu");
const closeUserMenu = document.querySelector(".close-user-menu");

if (openUserMenu && userMenu) {
  openUserMenu.addEventListener("click", () => {
    userMenu.classList.add("active");
  });
}

if (closeUserMenu && userMenu) {
  closeUserMenu.addEventListener("click", () => {
    userMenu.classList.remove("active");
  });
}

// TABS MODULE
document.addEventListener("DOMContentLoaded", function () {
  const tabs = document.querySelectorAll(".tab-button");
  const contents = document.querySelectorAll(".tab-content");

  // Check if elements exist
  if (!tabs.length || !contents.length) return;

  // Initialize first tab
  activateTab(tabs[0], contents[0]);

  // Add click handlers
  tabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const tabId =
        this.dataset.tab || this.getAttribute("onclick").match(/'([^']+)'/)[1];
      const content = document.getElementById(tabId);

      if (!content) {
        console.error("Content element not found for tab:", tabId);
        return;
      }

      // Reset all tabs
      resetTabs(tabs, contents);

      // Activate current tab
      activateTab(this, content);
    });
  });

  function resetTabs(tabsArray, contentsArray) {
    tabsArray.forEach((t) => {
      t.classList.remove("active", "text-primary-800", "border-primary-800");
    });

    contentsArray.forEach((c) => c.classList.add("hidden"));
  }

  function activateTab(tabElement, contentElement) {
    tabElement.classList.add(
      "active",
      "text-primary-800",
      "border-primary-800",
    );
    tabElement.classList.remove("bg-white");
    contentElement.classList.remove("hidden");
  }
});

// PRICE RANGE
document.querySelectorAll(".price-slider").forEach((sliderContainer) => {
  const priceElements = sliderContainer.querySelectorAll(".price-input p");
  const rangeInputs = sliderContainer.querySelectorAll(".range-input input");
  const range = sliderContainer.querySelector(".slider-bar .progress");
  let priceGap = 1000;

  function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  rangeInputs.forEach((input) => {
    input.addEventListener("input", (e) => {
      let minVal = parseInt(rangeInputs[0].value) * 10;
      let maxVal = parseInt(rangeInputs[1].value) * 10;

      if (maxVal - minVal < priceGap) {
        if (e.target.classList.contains("min-range")) {
          rangeInputs[0].value = (maxVal - priceGap) / 10;
        } else {
          rangeInputs[1].value = (minVal + priceGap) / 10;
        }
      } else {
        priceElements[0].textContent = formatNumber(minVal);
        priceElements[1].textContent = formatNumber(maxVal);
        range.style.left =
          (rangeInputs[0].value / rangeInputs[0].max) * 100 + "%";
        range.style.right =
          100 - (rangeInputs[1].value / rangeInputs[1].max) * 100 + "%";
      }
    });
  });
});

// SOERT MODALS - SHOP PAGE
const sortModal = document.querySelector(".sort-modal");
const sortModalOpen = document.querySelector(".sort-modal-open");
const sortModalClose = document.querySelector(".sort-modal-close");

sortModalOpen?.addEventListener("click", () => {
  sortModal.classList.add("active");
});

sortModalClose?.addEventListener("click", () => {
  sortModal.classList.remove("active");
});

// FILTER MODALS - SHOP PAGE
const filterModal = document.querySelector(".filter-modal");
const filterModalOpen = document.querySelector(".filter-modal-open");
const filterModalClose = document.querySelector(".filter-modal-close");

filterModalOpen?.addEventListener("click", () => {
  filterModal.classList.add("active");
});

filterModalClose?.addEventListener("click", () => {
  filterModal.classList.remove("active");
});

console.log(
  "%cUI_Flow",
  "background: #bc7bfd; color: white; font-size: 20px; font-weight: bold; padding: 5px 10px; border-radius: 5px;",
);

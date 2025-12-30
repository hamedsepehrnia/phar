import Swiper from "swiper";
import {
  Navigation,
  Pagination,
  Autoplay,
  EffectFade,
  Keyboard,
  Thumbs,
} from "swiper/modules";
import "swiper/css";
import "swiper/css/navigation";
import "swiper/css/pagination";
import "swiper/css/effect-fade";

Swiper.use([Navigation, Pagination, Autoplay, EffectFade, Keyboard, Thumbs]);

const swiper = new Swiper(".default-carousel", {
  loop: true,
  speed: 800,
  autoplay: {
    delay: 4000,
    disableOnInteraction: false,
  },
  effect: "fade", // fade باعث میشه اسلایدهای کناری دیده نشن
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
    dynamicBullets: true,
  },
  navigation: {
    nextEl: ".button-next",
    prevEl: ".button-prev",
  },
  grabCursor: true,
  keyboard: {
    enabled: true,
  },
  breakpoints: {
    320: {
      slidesPerView: 1, // کمی بیشتر از 1 برای اینکه بعدی دیده بشه
    },
    768: {
      slidesPerView: 1,
      spaceBetween: 0,
      centeredSlides: false,
    },
    1024: {
      slidesPerView: 1,
      spaceBetween: 0,
      centeredSlides: false,
    },
  },
});

const swiperCategory = new Swiper(".category-shortcut", {
  slidesPerView: 4.3,
  spaceBetween: 12,
  gap: 5,
  breakpoints: {
    575.98: {
      slidesPerView: 4,
    },
    767.98: {
      slidesPerView: 6,
    },
    991.98: {
      slidesPerView: 6,
    },
    1199.98: {
      slidesPerView: 7,
    },
    1399.98: {
      slidesPerView: 8,
    },
  },
});

const swiperProduct = new Swiper(".swiper-product", {
  loop: true,
  speed: 800,
  spaceBetween: 6,
  autoplay: {
    delay: 3000,
    disableOnInteraction: false,
  },
  effect: "slide",
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
    dynamicBullets: true,
  },
  navigation: {
    nextEl: ".button-next",
    prevEl: ".button-prev",
  },
  grabCursor: true,
  keyboard: {
    enabled: true,
  },
  breakpoints: {
    320: {
      slidesPerView: 1.4,
      spaceBetween: 12,
    },
    768: {
      slidesPerView: 2.6,
    },
    1024: {
      slidesPerView: 3.6,
    },
  },
});

const bestSellers = new Swiper(".best-sellers", {
  loop: true,
  speed: 800,
  spaceBetween: 6,
  autoplay: {
    delay: 4000,
    disableOnInteraction: false,
  },
  effect: "slide",
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
    dynamicBullets: true,
  },
  navigation: {
    nextEl: ".button-next",
    prevEl: ".button-prev",
  },
  grabCursor: true,
  keyboard: {
    enabled: true,
  },
  breakpoints: {
    320: {
      slidesPerView: 1.4,
      spaceBetween: 12,
    },
    768: {
      slidesPerView: 2.6,
    },
    1024: {
      slidesPerView: 5,
    },
  },
});

const newProduct = new Swiper(".new-product", {
  loop: true,
  speed: 800,
  spaceBetween: 6,
  autoplay: {
    delay: 3000,
    disableOnInteraction: false,
  },
  effect: "slide",
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
    dynamicBullets: true,
  },
  navigation: {
    nextEl: ".button-next",
    prevEl: ".button-prev",
  },
  grabCursor: true,
  keyboard: {
    enabled: true,
  },
  breakpoints: {
    320: {
      slidesPerView: 1.4,
      spaceBetween: 12,
    },
    768: {
      slidesPerView: 2.6,
    },
    1024: {
      slidesPerView: 5,
    },
  },
});

const productRelation = new Swiper(".product-relation", {
  loop: true,
  speed: 800,
  spaceBetween: 6,
  autoplay: {
    delay: 3000,
    disableOnInteraction: false,
  },
  effect: "slide",
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
    dynamicBullets: true,
  },
  navigation: {
    nextEl: ".button-next",
    prevEl: ".button-prev",
  },
  grabCursor: true,
  keyboard: {
    enabled: true,
  },
  breakpoints: {
    320: {
      slidesPerView: 1.4,
      spaceBetween: 12,
    },
    768: {
      slidesPerView: 2.6,
    },
    1024: {
      slidesPerView: 4.6,
    },
  },
});

const customSwiperNext = document.querySelector(".custom-swiper-next");
const customSwiperPrev = document.querySelector(".custom-swiper-prev");

if (customSwiperNext || customSwiperPrev) {
  customSwiperNext.addEventListener("click", () => {
    swiper.slideNext();
  });

  customSwiperPrev.addEventListener("click", () => {
    swiper.slidePrev();
  });
}

var swiperProductGalleryOne = new Swiper("#productGalleryOne", {
  spaceBetween: 10,
  slidesPerView: 5,
  freeMode: true,
  watchSlidesProgress: true,
});
var swiperProductGalleryTwo = new Swiper("#productGalleryTwo", {
  spaceBetween: 10,
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
  thumbs: {
    swiper: swiperProductGalleryOne,
  },
});

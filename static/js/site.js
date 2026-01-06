/**
 * Site Interactions - Pure JavaScript (No Alpine.js)
 */

document.addEventListener('DOMContentLoaded', function() {
  
  // ========== Preloader ==========
  const preloader = document.getElementById('preloader');
  if (preloader) {
    if (!localStorage.getItem('site_loaded')) {
      setTimeout(() => {
        preloader.style.display = 'none';
        localStorage.setItem('site_loaded', 'true');
      }, 500);
    } else {
      preloader.style.display = 'none';
    }
  }

  // ========== Mobile Search Panel ==========
  const mobileSearchTrigger = document.getElementById('mobile-search-trigger');
  const mobileSearchPanel = document.getElementById('mobile-search-panel');
  const mobileSearchClose = document.getElementById('mobile-search-close');

  if (mobileSearchTrigger && mobileSearchPanel) {
    mobileSearchTrigger.addEventListener('click', () => {
      mobileSearchPanel.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  }

  if (mobileSearchClose && mobileSearchPanel) {
    mobileSearchClose.addEventListener('click', () => {
      mobileSearchPanel.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  // ========== Desktop Account Dropdown ==========
  const accountDropdown = document.getElementById('account-dropdown');
  const accountMenu = document.getElementById('account-menu');
  const accountBtn = document.getElementById('account-btn');

  if (accountBtn && accountMenu) {
    accountBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      accountMenu.classList.toggle('hidden');
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!accountDropdown?.contains(e.target)) {
        accountMenu.classList.add('hidden');
      }
    });
  }

  // ========== Mega Menu ==========
  const megaMenuTrigger = document.getElementById('mega-menu-trigger');
  const megaMenu = document.getElementById('mega-menu');
  const megaMenuOverlay = document.getElementById('desktop-mega-menu-overlay');

  if (megaMenuTrigger && megaMenu) {
    megaMenuTrigger.addEventListener('mouseenter', () => {
      megaMenu.classList.remove('hidden');
      megaMenuOverlay?.classList.remove('hidden');
    });

    megaMenuTrigger.addEventListener('mouseleave', () => {
      megaMenu.classList.add('hidden');
      megaMenuOverlay?.classList.add('hidden');
    });

    megaMenu.addEventListener('mouseenter', () => {
      megaMenu.classList.remove('hidden');
    });

    megaMenu.addEventListener('mouseleave', () => {
      megaMenu.classList.add('hidden');
      megaMenuOverlay?.classList.add('hidden');
    });
  }

  // Mega menu category hover
  const megaMenuCategories = document.querySelectorAll('.mega-menu-category');
  const megaMenuSubcategories = document.querySelectorAll('.mega-menu-subcategory');

  megaMenuCategories.forEach((cat, index) => {
    cat.addEventListener('mouseenter', () => {
      // Remove active from all
      megaMenuCategories.forEach(c => c.classList.remove('mega-menu-link-active', 'text-primary-800', 'font-semibold'));
      megaMenuSubcategories.forEach(s => {
        s.classList.add('opacity-0', 'pointer-events-none');
        s.classList.remove('opacity-100', 'pointer-events-auto');
      });
      
      // Add active to current
      cat.classList.add('mega-menu-link-active', 'text-primary-800', 'font-semibold');
      const targetSub = document.querySelector(`.mega-menu-subcategory[data-index="${index}"]`);
      if (targetSub) {
        targetSub.classList.remove('opacity-0', 'pointer-events-none');
        targetSub.classList.add('opacity-100', 'pointer-events-auto');
      }
    });
  });

  // ========== Mobile Dashboard Sidebar ==========
  const mobileSidebarBtn = document.getElementById('mobile-sidebar-btn');
  const mobileSidebar = document.getElementById('mobile-sidebar');
  const mobileSidebarOverlay = document.getElementById('mobile-sidebar-overlay');
  const mobileSidebarClose = document.getElementById('mobile-sidebar-close');

  if (mobileSidebarBtn && mobileSidebar) {
    mobileSidebarBtn.addEventListener('click', () => {
      mobileSidebar.classList.remove('hidden');
      mobileSidebarOverlay?.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    });
  }

  if (mobileSidebarClose && mobileSidebar) {
    mobileSidebarClose.addEventListener('click', () => {
      mobileSidebar.classList.add('hidden');
      mobileSidebarOverlay?.classList.add('hidden');
      document.body.style.overflow = '';
    });
  }

  if (mobileSidebarOverlay && mobileSidebar) {
    mobileSidebarOverlay.addEventListener('click', () => {
      mobileSidebar.classList.add('hidden');
      mobileSidebarOverlay.classList.add('hidden');
      document.body.style.overflow = '';
    });
  }

  // ========== Product Gallery ==========
  const productThumbs = document.querySelectorAll('.product-thumb');
  const productMainImages = document.querySelectorAll('.product-main-image');

  productThumbs.forEach((thumb, index) => {
    thumb.addEventListener('click', () => {
      productMainImages.forEach(img => img.classList.add('hidden'));
      productThumbs.forEach(t => t.classList.remove('border-primary-800'));
      
      const targetImage = document.querySelector(`.product-main-image[data-index="${index}"]`);
      if (targetImage) {
        targetImage.classList.remove('hidden');
      }
      thumb.classList.add('border-primary-800');
    });
  });

  // ========== Quantity Buttons ==========
  document.querySelectorAll('.quantity-minus').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.parentElement.querySelector('input[type="number"]');
      if (input && parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
      }
    });
  });

  document.querySelectorAll('.quantity-plus').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.parentElement.querySelector('input[type="number"]');
      const max = parseInt(input?.getAttribute('max') || '999');
      if (input && parseInt(input.value) < max) {
        input.value = parseInt(input.value) + 1;
      }
    });
  });

  // ========== Star Rating ==========
  const ratingStars = document.querySelectorAll('.rating-star');
  const ratingInput = document.getElementById('rating-input');

  ratingStars.forEach((star, index) => {
    star.addEventListener('click', () => {
      const rating = index + 1;
      if (ratingInput) ratingInput.value = rating;
      
      ratingStars.forEach((s, i) => {
        if (i < rating) {
          s.classList.add('text-yellow-500');
          s.classList.remove('text-gray-300');
        } else {
          s.classList.remove('text-yellow-500');
          s.classList.add('text-gray-300');
        }
      });
    });
  });

  // ========== OTP Timer ==========
  const otpTimer = document.getElementById('otp-timer');
  const resendBtn = document.getElementById('resend-otp-btn');
  
  if (otpTimer) {
    let timeLeft = parseInt(otpTimer.dataset.time || '180');
    
    const updateTimer = () => {
      const minutes = Math.floor(timeLeft / 60);
      const seconds = timeLeft % 60;
      otpTimer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
      
      if (timeLeft > 0) {
        timeLeft--;
        setTimeout(updateTimer, 1000);
      } else {
        if (resendBtn) {
          resendBtn.disabled = false;
          resendBtn.classList.remove('opacity-50');
        }
      }
    };
    
    updateTimer();
  }

});

// ========== CSS for animations ==========
const style = document.createElement('style');
style.textContent = `
  #mobile-search-panel {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: white;
    padding: 2.5rem 1rem;
    transform: translateY(100%);
    transition: transform 0.3s ease-out;
  }
  #mobile-search-panel.active {
    transform: translateY(0);
  }
  #mega-menu {
    transition: opacity 0.2s ease;
  }
`;
document.head.appendChild(style);

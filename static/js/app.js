/**
 * Pharmacy E-Commerce - Main Application Script
 * Works with Alpine.js for reactive components
 */

(function() {
    'use strict';

    // ==================== UTILITY FUNCTIONS ====================
    
    function formatFaNumber(num) {
        return new Intl.NumberFormat('fa-IR').format(num);
    }

    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    function qs(selector, parent = document) {
        return parent.querySelector(selector);
    }

    function qsa(selector, parent = document) {
        return Array.from(parent.querySelectorAll(selector));
    }

    // ==================== ALPINE COMPONENTS ====================
    
    document.addEventListener('alpine:init', () => {
        // OTP Timer Component
        Alpine.data('otpTimer', () => ({
            timeLeft: 180,
            init() {
                this.startTimer();
            },
            startTimer() {
                const interval = setInterval(() => {
                    this.timeLeft--;
                    if (this.timeLeft <= 0) {
                        clearInterval(interval);
                    }
                }, 1000);
            },
            formatTime() {
                const minutes = Math.floor(this.timeLeft / 60);
                const seconds = this.timeLeft % 60;
                return minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
            }
        }));

        // Countdown Component
        Alpine.data('countdown', (targetDate) => ({
            days: 0,
            hours: 0,
            minutes: 0,
            seconds: 0,
            timer: null,
            init() {
                this.start();
            },
            update() {
                const now = new Date().getTime();
                const target = new Date(targetDate).getTime();
                const diff = target - now;

                if (diff <= 0) {
                    this.days = this.hours = this.minutes = this.seconds = 0;
                    if (this.timer) clearInterval(this.timer);
                    return;
                }

                this.days = Math.floor(diff / (1000 * 60 * 60 * 24));
                this.hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                this.minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                this.seconds = Math.floor((diff % (1000 * 60)) / 1000);
            },
            start() {
                this.update();
                this.timer = setInterval(() => this.update(), 1000);
            }
        }));

        // Price Range Component
        Alpine.data('priceRange', () => ({
            min: 0,
            max: 35000,
            priceGap: 1000,
            minPercent: 0,
            maxPercent: 100,
            formatNumber(num) {
                return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
            },
            updateMin() {
                if (this.max - this.min < this.priceGap) {
                    this.min = this.max - this.priceGap;
                }
                this.updatePercent();
            },
            updateMax() {
                if (this.max - this.min < this.priceGap) {
                    this.max = this.min + this.priceGap;
                }
                this.updatePercent();
            },
            updatePercent() {
                this.minPercent = (this.min / 100000) * 100;
                this.maxPercent = (this.max / 100000) * 100;
            }
        }));
    });

    // ==================== PERSIAN NUMBER CONVERSION ====================
    
    qsa('.fa-number').forEach(el => {
        const rawNumber = el.innerText.trim();
        el.innerText = formatFaNumber(rawNumber);
    });

    // ==================== USER MENU ====================
    
    const userMenu = qs('.user-menu');
    const openUserMenu = qs('.open-user-menu');
    const closeUserMenu = qs('.close-user-menu');

    if (openUserMenu && userMenu) {
        openUserMenu.addEventListener('click', () => {
            userMenu.classList.add('active');
        });
    }

    if (closeUserMenu && userMenu) {
        closeUserMenu.addEventListener('click', () => {
            userMenu.classList.remove('active');
        });
    }

    // ==================== TABS MODULE ====================
    
    function initTabs() {
        const tabs = qsa('.tab-button');
        const contents = qsa('.tab-content');

        if (!tabs.length || !contents.length) return;

        activateTab(tabs[0], contents[0]);

        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabId = this.dataset.tab || this.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
                const content = document.getElementById(tabId);

                if (!content) {
                    console.error('Content element not found for tab:', tabId);
                    return;
                }

                resetTabs(tabs, contents);
                activateTab(this, content);
            });
        });

        function resetTabs(tabsArray, contentsArray) {
            tabsArray.forEach(t => {
                t.classList.remove('active', 'text-primary-800', 'border-primary-800');
            });

            contentsArray.forEach(c => c.classList.add('hidden'));
        }

        function activateTab(tabElement, contentElement) {
            tabElement.classList.add('active', 'text-primary-800', 'border-primary-800');
            tabElement.classList.remove('bg-white');
            contentElement.classList.remove('hidden');
        }
    }

    // ==================== PRICE RANGE SLIDER ====================
    
    function initPriceRangeSliders() {
        qsa('.price-slider').forEach(sliderContainer => {
            const priceElements = qsa('.price-input p', sliderContainer);
            const rangeInputs = qsa('.range-input input', sliderContainer);
            const range = qs('.slider-bar .progress', sliderContainer);
            const priceGap = 1000;

            rangeInputs.forEach(input => {
                input.addEventListener('input', e => {
                    let minVal = parseInt(rangeInputs[0].value) * 10;
                    let maxVal = parseInt(rangeInputs[1].value) * 10;

                    if (maxVal - minVal < priceGap) {
                        if (e.target.classList.contains('min-range')) {
                            rangeInputs[0].value = (maxVal - priceGap) / 10;
                        } else {
                            rangeInputs[1].value = (minVal + priceGap) / 10;
                        }
                    } else {
                        priceElements[0].textContent = formatNumber(minVal);
                        priceElements[1].textContent = formatNumber(maxVal);
                        range.style.left = (rangeInputs[0].value / rangeInputs[0].max) * 100 + '%';
                        range.style.right = 100 - (rangeInputs[1].value / rangeInputs[1].max) * 100 + '%';
                    }
                });
            });
        });
    }

    // ==================== MODALS ====================
    
    function initModals() {
        const sortModal = qs('.sort-modal');
        const sortModalOpen = qs('.sort-modal-open');
        const sortModalClose = qs('.sort-modal-close');

        sortModalOpen?.addEventListener('click', () => {
            sortModal.classList.add('active');
        });

        sortModalClose?.addEventListener('click', () => {
            sortModal.classList.remove('active');
        });

        const filterModal = qs('.filter-modal');
        const filterModalOpen = qs('.filter-modal-open');
        const filterModalClose = qs('.filter-modal-close');

        filterModalOpen?.addEventListener('click', () => {
            filterModal.classList.add('active');
        });

        filterModalClose?.addEventListener('click', () => {
            filterModal.classList.remove('active');
        });
    }

    // ==================== LAZY LOADING IMAGES ====================
    
    function initLazyImages() {
        const images = qsa('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // ==================== SMOOTH SCROLL ====================
    
    function initSmoothScroll() {
        qsa('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;
                
                const target = document.getElementById(href.slice(1));
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    }

    // ==================== INITIALIZATION ====================
    
    function init() {
        initTabs();
        initPriceRangeSliders();
        initModals();
        initLazyImages();
        initSmoothScroll();

        console.log('%c✅ Pharmacy App Ready', 
            'background: #10b981; color: white; font-size: 14px; font-weight: bold; padding: 4px 8px; border-radius: 4px;'
        );
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

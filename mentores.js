document.addEventListener('DOMContentLoaded', () => {
    /* ================= MENTORES SLIDER & AUTO-RESIZE ================= */
    const mentorsTrack = document.getElementById('mentors-track');
    if (!mentorsTrack) return;

    const mentorCards = document.querySelectorAll('#mentors-track .mentor-card');
    const btnMentorsPrev = document.getElementById('mentors-prev');
    const btnMentorsNext = document.getElementById('mentors-next');
    const dotsContainer = document.getElementById('mentors-dots');

    let currentIndex = 0;
    const totalCards = mentorCards.length;

    function getCardsPerView() {
        if (window.innerWidth > 1024) return 4;
        if (window.innerWidth > 768) return 3;
        if (window.innerWidth > 480) return 2;
        return 1;
    }

    function getMaxIndex() {
        const cardsPerView = getCardsPerView();
        return Math.max(0, totalCards - cardsPerView);
    }

    function renderDots() {
        if (!dotsContainer || !totalCards) return;
        dotsContainer.innerHTML = '';

        const cardsPerView = getCardsPerView();
        const maxIndex = getMaxIndex();
        const step = Math.max(1, Math.floor(cardsPerView));

        let pageIndices = [];
        for (let i = 0; i < totalCards; i += step) {
            pageIndices.push(Math.min(maxIndex, i));
            if (i + step >= totalCards && pageIndices[pageIndices.length - 1] !== maxIndex) {
                pageIndices.push(maxIndex);
            }
        }
        // Remove duplicates
        pageIndices = Array.from(new Set(pageIndices));

        pageIndices.forEach((idx, pageNum) => {
            const dot = document.createElement('button');
            dot.className = 'mentor-dot' + (idx === currentIndex ? ' active' : '');
            dot.setAttribute('data-index', idx);
            dot.setAttribute('aria-label', `Ir para página de mentores ${pageNum + 1}`);
            dot.addEventListener('click', () => {
                currentIndex = idx;
                updateSlider();
            });
            dotsContainer.appendChild(dot);
        });
    }

    function updateSlider() {
        const cardsPerView = getCardsPerView();
        const maxIndex = getMaxIndex();

        if (currentIndex > maxIndex) currentIndex = maxIndex;
        if (currentIndex < 0) currentIndex = 0;

        const gap = window.innerWidth > 768 ? 24 : (window.innerWidth > 480 ? 20 : 16);
        const pct = (currentIndex / cardsPerView) * 100;
        const px = currentIndex * (gap / cardsPerView);
        mentorsTrack.style.transform = `translateX(calc(-${pct}% - ${px}px))`;

        // Arrow button states
        if (btnMentorsPrev) {
            btnMentorsPrev.style.opacity = currentIndex === 0 ? '0.35' : '1';
            btnMentorsPrev.style.pointerEvents = currentIndex === 0 ? 'none' : 'auto';
        }
        if (btnMentorsNext) {
            btnMentorsNext.style.opacity = currentIndex === maxIndex ? '0.35' : '1';
            btnMentorsNext.style.pointerEvents = currentIndex === maxIndex ? 'none' : 'auto';
        }

        // Active dot update
        const dots = dotsContainer ? dotsContainer.querySelectorAll('.mentor-dot') : [];
        let activeIdx = 0;
        let minDiff = Infinity;

        dots.forEach((dot, index) => {
            const dotIdx = parseInt(dot.getAttribute('data-index'), 10);
            const diff = Math.abs(dotIdx - currentIndex);
            if (diff < minDiff) {
                minDiff = diff;
                activeIdx = index;
            }
            dot.classList.remove('active');
        });

        if (dots[activeIdx]) {
            dots[activeIdx].classList.add('active');
        }
    }

    // Arrow Button Handlers
    if (btnMentorsPrev) {
        btnMentorsPrev.addEventListener('click', () => {
            const cardsPerView = getCardsPerView();
            currentIndex = Math.max(0, currentIndex - cardsPerView);
            updateSlider();
        });
    }

    if (btnMentorsNext) {
        btnMentorsNext.addEventListener('click', () => {
            const cardsPerView = getCardsPerView();
            const maxIndex = getMaxIndex();
            currentIndex = Math.min(maxIndex, currentIndex + cardsPerView);
            updateSlider();
        });
    }

    // Touch Swipe Gestures
    let touchStartX = 0;
    let touchEndX = 0;

    mentorsTrack.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });

    mentorsTrack.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });

    function handleSwipe() {
        const swipeThreshold = 45;
        const diff = touchStartX - touchEndX;
        const cardsPerView = getCardsPerView();
        const maxIndex = getMaxIndex();

        if (diff > swipeThreshold) {
            if (currentIndex < maxIndex) {
                currentIndex = Math.min(maxIndex, currentIndex + 1);
                updateSlider();
            }
        } else if (diff < -swipeThreshold) {
            if (currentIndex > 0) {
                currentIndex = Math.max(0, currentIndex - 1);
                updateSlider();
            }
        }
    }

    // Window Resize Handler
    window.addEventListener('resize', () => {
        renderDots();
        updateSlider();
    });

    // Auto-Resize Support when embedded via <iframe>
    function notifyParentHeight() {
        if (window.parent && window.parent !== window) {
            const sectionEl = document.getElementById('mentores') || document.body;
            const height = Math.ceil(sectionEl.getBoundingClientRect().height);
            window.parent.postMessage({ type: 'inatel-mentors-resize', height: height }, '*');
        }
    }

    if (typeof ResizeObserver !== 'undefined') {
        const ro = new ResizeObserver(() => notifyParentHeight());
        ro.observe(document.body);
    }
    window.addEventListener('load', notifyParentHeight);

    // Initial setup
    renderDots();
    updateSlider();
    setTimeout(notifyParentHeight, 150);
});

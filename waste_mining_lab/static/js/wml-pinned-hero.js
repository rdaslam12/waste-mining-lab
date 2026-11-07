/* Homepage research messages: lightweight, visibility-aware rotation. */
(() => {
    const hero = document.querySelector("[data-pinned-hero]");
    if (!hero) return;

    const slides = Array.from(hero.querySelectorAll("[data-hero-slide]"));
    const dots = Array.from(hero.querySelectorAll("[data-hero-dot]"));
    const toggle = hero.querySelector("[data-hero-toggle]");
    if (slides.length < 2) return;

    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const intervalMs = 7000;
    let current = 0;
    let timer = null;
    let userPaused = reducedMotion.matches;
    let inView = true;

    function showSlide(index) {
        current = (index + slides.length) % slides.length;

        slides.forEach((slide, slideIndex) => {
            const isActive = slideIndex === current;
            slide.classList.toggle("is-active", isActive);
            slide.setAttribute("aria-hidden", String(!isActive));
        });

        dots.forEach((dot, dotIndex) => {
            const isActive = dotIndex === current;
            dot.classList.toggle("is-active", isActive);
            dot.setAttribute("aria-pressed", String(isActive));
        });
    }

    function stopTimer() {
        if (timer !== null) window.clearTimeout(timer);
        timer = null;
    }

    function updateToggle() {
        if (!toggle) return;

        toggle.hidden = reducedMotion.matches;
        toggle.textContent = userPaused ? "Play" : "Pause";
        toggle.setAttribute("aria-pressed", String(userPaused));
        toggle.setAttribute(
            "aria-label",
            userPaused ? "Play rotating messages" : "Pause rotating messages"
        );
    }

    function scheduleNext() {
        stopTimer();
        updateToggle();

        if (userPaused || reducedMotion.matches || document.hidden || !inView) return;

        timer = window.setTimeout(() => {
            showSlide(current + 1);
            scheduleNext();
        }, intervalMs);
    }

    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => {
            showSlide(index);
            scheduleNext();
        });
    });

    if (toggle) {
        toggle.addEventListener("click", () => {
            userPaused = !userPaused;
            scheduleNext();
        });
    }

    document.addEventListener("visibilitychange", scheduleNext);

    const handleMotionChange = () => {
        userPaused = reducedMotion.matches;
        showSlide(0);
        scheduleNext();
    };

    if (typeof reducedMotion.addEventListener === "function") {
        reducedMotion.addEventListener("change", handleMotionChange);
    } else {
        reducedMotion.addListener(handleMotionChange);
    }

    if ("IntersectionObserver" in window) {
        const observer = new IntersectionObserver((entries) => {
            inView = entries[0]?.isIntersecting ?? true;
            scheduleNext();
        }, { threshold: 0.1 });
        observer.observe(hero);
    }

    hero.classList.add("has-rotation");
    showSlide(0);
    scheduleNext();
})();

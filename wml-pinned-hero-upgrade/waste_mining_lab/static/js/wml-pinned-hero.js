/* Rotating hero messages: no library required. */
(() => {
    function initHero() {
        const hero = document.querySelector(".wml-pinned-hero");
        if (!hero) return;

        const slides = Array.from(hero.querySelectorAll("[data-hero-slide]"));
        const dots = Array.from(hero.querySelectorAll("[data-hero-dot]"));
        const toggle = hero.querySelector("[data-hero-toggle]");
        if (slides.length < 2) return;

        const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
        const INTERVAL_MS = 7000;
        let current = 0;
        let timer = null;
        let manuallyPaused = reducedMotion.matches;
        let inView = true;

        function showSlide(index) {
            current = (index + slides.length) % slides.length;
            slides.forEach((slide, i) => {
                const active = i === current;
                slide.classList.toggle("is-active", active);
                slide.setAttribute("aria-hidden", String(!active));
            });
            dots.forEach((dot, i) => {
                dot.classList.toggle("is-active", i === current);
                dot.setAttribute("aria-pressed", String(i === current));
            });
        }

        function stop() {
            if (timer !== null) window.clearInterval(timer);
            timer = null;
        }

        function syncTimer() {
            stop();
            if (!manuallyPaused && !document.hidden && inView && !reducedMotion.matches) {
                timer = window.setInterval(() => showSlide(current + 1), INTERVAL_MS);
            }
            if (toggle) {
                toggle.hidden = reducedMotion.matches;
                toggle.textContent = manuallyPaused ? "Play" : "Pause";
                toggle.setAttribute(
                    "aria-label",
                    manuallyPaused ? "Play rotating messages" : "Pause rotating messages"
                );
            }
        }

        dots.forEach((dot, i) => {
            dot.addEventListener("click", () => {
                showSlide(i);
                syncTimer();
            });
        });

        if (toggle) {
            toggle.addEventListener("click", () => {
                manuallyPaused = !manuallyPaused;
                syncTimer();
            });
        }

        document.addEventListener("visibilitychange", syncTimer);
        reducedMotion.addEventListener("change", () => {
            manuallyPaused = reducedMotion.matches;
            syncTimer();
        });

        if ("IntersectionObserver" in window) {
            const observer = new IntersectionObserver(entries => {
                inView = entries[0]?.isIntersecting ?? true;
                syncTimer();
            }, {threshold: 0.1});
            observer.observe(hero);
        }

        hero.classList.add("has-rotation");
        showSlide(0);
        syncTimer();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initHero);
    } else {
        initHero();
    }
})();

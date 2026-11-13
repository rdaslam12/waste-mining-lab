(() => {
    const section = document.querySelector('[data-faculty]');
    if (!section || !('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const observer = new IntersectionObserver((entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
            section.classList.add('is-entering');
            observer.disconnect();
        }
    }, { threshold: 0.12 });
    observer.observe(section);
})();

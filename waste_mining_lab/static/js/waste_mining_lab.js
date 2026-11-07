// Waste Mining Lab: stable compact navigation.
// The expanded header remains in document flow, so toggling the fixed bar
// does not change page height or cause scroll threshold oscillation.
document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".wml-global-header");
    if (!header) return;

    const mobileMenu = header.querySelector(".wml-mobile-menu");
    let animationFrame = null;

    function updateHeader() {
        if (animationFrame !== null) return;
        animationFrame = window.requestAnimationFrame(() => {
            animationFrame = null;
            header.classList.toggle("is-scrolled", window.scrollY > 90);
        });
    }

    window.addEventListener("scroll", updateHeader, { passive: true });
    window.addEventListener("pageshow", updateHeader);
    window.addEventListener("resize", updateHeader);

    if (mobileMenu) {
        mobileMenu.addEventListener("toggle", () => {
            header.classList.toggle("menu-open", mobileMenu.open);
        });
    }

    updateHeader();
});


document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".wml-global-header");
    if (!header) return;

    const mobileMenu = header.querySelector(".wml-mobile-menu");

    function updateHeader() {
        const scrolled = window.scrollY > 90;
        header.classList.toggle("is-scrolled", scrolled);
    }

    // Update on scrolling
    window.addEventListener("scroll", updateHeader, {
        passive: true
    });

    // Keep dropdown accessible
    if (mobileMenu) {
        mobileMenu.addEventListener("toggle", () => {
            header.classList.toggle("menu-open", mobileMenu.open);
        });
    }

    // Apply correct state on page load and refresh
    updateHeader();
});

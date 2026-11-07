
document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.querySelector(".wml-navbar");
    if (!navbar) return;

    const mobileMenu = navbar.querySelector(".wml-mobile-menu");

    function updateNavbar() {
        navbar.classList.toggle("is-scrolled", window.scrollY > 80);
    }

    window.addEventListener("scroll", updateNavbar, {
        passive: true
    });

    if (mobileMenu) {
        mobileMenu.addEventListener("toggle", () => {
            navbar.classList.toggle("menu-open", mobileMenu.open);
        });
    }

    updateNavbar();
});

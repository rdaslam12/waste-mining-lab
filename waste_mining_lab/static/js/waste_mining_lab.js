
document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.querySelector(".wml-navbar");
    if (!navbar) return;

    const mobileMenu = navbar.querySelector(".wml-mobile-menu");

    function updateNavbar() {
        const isScrolled = window.scrollY > 80;

        navbar.classList.toggle("is-scrolled", isScrolled);

        // Scrolling always returns the navbar to compact mode.
        navbar.classList.remove("is-expanded");
    }

    // Expand when the mouse moves over the compact navbar.
    navbar.addEventListener("pointermove", (event) => {
        if (event.pointerType === "mouse" &&
            navbar.classList.contains("is-scrolled")) {
            navbar.classList.add("is-expanded");
        }
    });

    // Shrink when the mouse leaves.
    navbar.addEventListener("pointerleave", () => {
        navbar.classList.remove("is-expanded");
    });

    // Keyboard accessibility.
    navbar.addEventListener("focusin", () => {
        if (navbar.classList.contains("is-scrolled")) {
            navbar.classList.add("is-expanded");
        }
    });

    navbar.addEventListener("focusout", (event) => {
        if (!navbar.contains(event.relatedTarget)) {
            navbar.classList.remove("is-expanded");
        }
    });

    if (mobileMenu) {
        mobileMenu.addEventListener("toggle", () => {
            navbar.classList.toggle("menu-open", mobileMenu.open);
        });
    }

    window.addEventListener("scroll", updateNavbar, {
        passive: true
    });

    updateNavbar();
});

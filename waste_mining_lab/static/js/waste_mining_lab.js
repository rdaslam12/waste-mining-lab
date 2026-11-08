
document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".wml-global-header");
    if (!header) return;

    const mission = document.querySelector(".mission");
    const hamburgerBtn = header.querySelector(".wml-hamburger-btn");
    const mobileDrawer = header.querySelector(".wml-mobile-drawer");
    const drawerBackdrop = mobileDrawer ? mobileDrawer.querySelector(".wml-mobile-drawer-backdrop") : null;
    const drawerLinks = mobileDrawer ? mobileDrawer.querySelectorAll("a") : [];

    let animationFrame = null;
    let lastScrollY = window.scrollY;

    // Mobile Navigation Drawer Controller (Phase 7)
    function setDrawerState(open) {
        if (!hamburgerBtn || !mobileDrawer) return;

        hamburgerBtn.setAttribute("aria-expanded", open ? "true" : "false");
        hamburgerBtn.setAttribute("aria-label", open ? "Close navigation menu" : "Open navigation menu");
        mobileDrawer.classList.toggle("is-open", open);
        mobileDrawer.setAttribute("aria-hidden", open ? "false" : "true");
        header.classList.toggle("menu-open", open);

        if (open) {
            header.classList.remove("nav-hidden");
            document.body.style.overflow = "hidden";
            // Focus first link in drawer
            const firstLink = mobileDrawer.querySelector("a");
            if (firstLink) setTimeout(() => firstLink.focus(), 150);
        } else {
            document.body.style.overflow = "";
        }
    }

    if (hamburgerBtn && mobileDrawer) {
        hamburgerBtn.addEventListener("click", () => {
            const isOpen = hamburgerBtn.getAttribute("aria-expanded") === "true";
            setDrawerState(!isOpen);
        });

        if (drawerBackdrop) {
            drawerBackdrop.addEventListener("click", () => setDrawerState(false));
        }

        drawerLinks.forEach(link => {
            link.addEventListener("click", () => setDrawerState(false));
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && mobileDrawer.classList.contains("is-open")) {
                setDrawerState(false);
                hamburgerBtn.focus();
            }
        });
    }

    // Scroll and Header State Manager
    function updateHeader() {
        if (animationFrame !== null) return;

        animationFrame = requestAnimationFrame(() => {
            animationFrame = null;

            const currentY = window.scrollY;
            const scrollingUp = currentY < lastScrollY - 2;
            const isMenuOpen = mobileDrawer && mobileDrawer.classList.contains("is-open");

            header.classList.toggle("is-scrolled", currentY > 90);

            if (mission && !isMenuOpen) {
                const missionBottom = mission.getBoundingClientRect().bottom;
                const pastMission = missionBottom <= 400;

                header.classList.toggle(
                    "nav-hidden",
                    pastMission && !scrollingUp
                );
            } else if (isMenuOpen) {
                header.classList.remove("nav-hidden");
            }

            lastScrollY = currentY;
        });
    }

    window.addEventListener("scroll", updateHeader, { passive: true });
    window.addEventListener("resize", () => {
        if (window.innerWidth > 1024 && mobileDrawer && mobileDrawer.classList.contains("is-open")) {
            setDrawerState(false);
        }
        updateHeader();
    });
    window.addEventListener("pageshow", updateHeader);

    updateHeader();
});

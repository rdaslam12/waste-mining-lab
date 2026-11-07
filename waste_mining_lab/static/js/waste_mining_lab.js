
document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector(".wml-global-header");
    if (!header) return;

    const mission = document.querySelector(".mission");
    const mobileMenu = header.querySelector(".wml-mobile-menu");

    let animationFrame = null;
    let lastScrollY = window.scrollY;

    function updateHeader() {
        if (animationFrame !== null) return;

        animationFrame = requestAnimationFrame(() => {
            animationFrame = null;

            const currentY = window.scrollY;
            const scrollingUp = currentY < lastScrollY - 2;

            header.classList.toggle("is-scrolled", currentY > 90);

            if (mission) {
                const missionBottom =
                    mission.getBoundingClientRect().bottom;

                const pastMission = missionBottom <= 400;

                header.classList.toggle(
                    "nav-hidden",
                    pastMission &&
                    !scrollingUp &&
                    !(mobileMenu && mobileMenu.open)
                );
            }

            lastScrollY = currentY;
        });
    }

    window.addEventListener("scroll", updateHeader, {
        passive: true
    });

    window.addEventListener("resize", updateHeader);
    window.addEventListener("pageshow", updateHeader);

    if (mobileMenu) {
        mobileMenu.addEventListener("toggle", updateHeader);
    }

    updateHeader();
});

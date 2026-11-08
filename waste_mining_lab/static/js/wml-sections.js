/**
 * Waste Mining Lab — Editorial Section Interactions & Motion Engine
 * Lightweight, 60fps, Zero-dependency, Prefers-reduced-motion respectful
 */

(function () {
    "use strict";

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    document.addEventListener("DOMContentLoaded", () => {
        initScrollReveals();
        initPublicationInteractions();
        initDashboardMicroInteractions();
        initTeamAccordion();
        initProfileModals();
    });

    /**
     * Scroll-triggered reveals using IntersectionObserver
     */
    function initScrollReveals() {
        if (prefersReducedMotion) return;

        const revealElements = document.querySelectorAll(
            ".wml-editorial h1, .wml-editorial .lead, .wml-editorial .section-heading, " +
            ".wml-editorial .featured-publications, .wml-editorial .research-area, " +
            ".wml-editorial .project-feature, .wml-editorial .director-spotlight-card, " +
            ".wml-editorial .team-accordion-wrap, .wml-editorial .academic-member-card, " +
            ".wml-editorial .activity-entry, .wml-editorial .news-feature, " +
            ".wml-editorial .news-card, .wml-editorial .monitoring-platform, " +
            ".wml-editorial .contact-layout, .wml-editorial .editorial-cta"
        );

        if (!("IntersectionObserver" in window)) {
            revealElements.forEach(el => el.classList.add("is-revealed"));
            return;
        }

        const observer = new IntersectionObserver(
            (entries, obs) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-revealed");
                        obs.unobserve(entry.target);
                    }
                });
            },
            {
                rootMargin: "0px 0px -50px 0px",
                threshold: 0.08
            }
        );

        revealElements.forEach(el => {
            el.classList.add("wml-reveal");
            observer.observe(el);
        });

        // Stagger containers
        const staggerContainers = document.querySelectorAll(
            ".wml-editorial .research-areas, .wml-editorial .team-directory-grid, " +
            ".wml-editorial .news-grid, .wml-editorial .journal-topics ul, " +
            ".wml-editorial .grants-grid"
        );

        const staggerObserver = new IntersectionObserver(
            (entries, obs) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-revealed");
                        obs.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.05 }
        );

        staggerContainers.forEach(container => {
            container.classList.add("wml-stagger");
            staggerObserver.observe(container);
        });
    }

    /**
     * Publication archive interactions: keyboard focus and copy DOI/citation
     */
    function initPublicationInteractions() {
        const searchInput = document.getElementById("publication-search");
        if (searchInput) {
            document.addEventListener("keydown", (e) => {
                if (e.key === "/" && document.activeElement !== searchInput && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
                    e.preventDefault();
                    searchInput.focus();
                }
            });
        }
    }

    /**
     * Interactive Portrait Accordion (Phase 4 — Reference B)
     * Handles hover, click, touch, and keyboard selection smoothly
     */
    function initTeamAccordion() {
        const accordion = document.querySelector('[data-accordion="team"]');
        if (!accordion) return;

        const cards = Array.from(accordion.querySelectorAll(".team-accordion-card"));
        if (!cards.length) return;

        let activeIndex = cards.findIndex(c => c.classList.contains("is-active"));
        if (activeIndex === -1) {
            activeIndex = 0;
            cards[0].classList.add("is-active");
            cards[0].setAttribute("aria-expanded", "true");
        }

        function activateCard(index) {
            if (index < 0 || index >= cards.length) return;
            activeIndex = index;

            cards.forEach((card, idx) => {
                const isActive = idx === index;
                card.classList.toggle("is-active", isActive);
                card.setAttribute("aria-expanded", isActive ? "true" : "false");
            });
        }

        cards.forEach((card, index) => {
            // Mouse hover expansion (only for precision pointer devices)
            card.addEventListener("mouseenter", () => {
                if (window.matchMedia("(hover: hover) and (min-width: 769px)").matches) {
                    activateCard(index);
                }
            });

            // Click or tap expansion
            card.addEventListener("click", (e) => {
                // If user clicks a button or link inside the card, don't interfere
                if (e.target.closest("button") || e.target.closest("a")) {
                    return;
                }
                activateCard(index);
            });

            // Keyboard navigation (Enter / Space to activate, Arrow keys to navigate)
            card.addEventListener("keydown", (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    if (e.target.closest("button") || e.target.closest("a")) return;
                    e.preventDefault();
                    activateCard(index);
                } else if (e.key === "ArrowRight" || e.key === "ArrowDown") {
                    e.preventDefault();
                    const next = (index + 1) % cards.length;
                    cards[next].focus();
                    activateCard(next);
                } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
                    e.preventDefault();
                    const prev = (index - 1 + cards.length) % cards.length;
                    cards[prev].focus();
                    activateCard(prev);
                }
            });
        });
    }

    /**
     * Accessible Profile Modals for Academic Team Members (Phase 4.4)
     */
    function initProfileModals() {
        let activeModal = null;
        let lastFocusedElement = null;

        function openModal(modalId) {
            const modal = document.getElementById(modalId);
            if (!modal) return;

            lastFocusedElement = document.activeElement;
            activeModal = modal;
            modal.removeAttribute("hidden");
            modal.classList.add("is-visible");
            document.body.style.overflow = "hidden";

            // Focus the close button or first focusable element inside modal
            const closeBtn = modal.querySelector(".modal-close-btn");
            if (closeBtn) {
                setTimeout(() => closeBtn.focus(), 80);
            }
        }

        function closeModal(modal) {
            if (!modal) return;
            modal.classList.remove("is-visible");
            setTimeout(() => {
                modal.setAttribute("hidden", "");
            }, 250);

            document.body.style.overflow = "";
            activeModal = null;

            if (lastFocusedElement) {
                lastFocusedElement.focus();
                lastFocusedElement = null;
            }
        }

        // Trigger buttons
        document.addEventListener("click", (e) => {
            const trigger = e.target.closest("[data-open-modal]");
            if (trigger) {
                e.preventDefault();
                const modalId = trigger.getAttribute("data-open-modal");
                openModal(modalId);
                return;
            }

            const closer = e.target.closest("[data-close-modal]");
            if (closer && activeModal) {
                e.preventDefault();
                closeModal(activeModal);
            }
        });

        // Keyboard Escape key and Focus Trap
        document.addEventListener("keydown", (e) => {
            if (!activeModal) return;

            if (e.key === "Escape") {
                e.preventDefault();
                closeModal(activeModal);
                return;
            }

            if (e.key === "Tab") {
                const focusables = Array.from(activeModal.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                )).filter(el => !el.hasAttribute("disabled") && el.offsetParent !== null);

                if (!focusables.length) return;

                const firstEl = focusables[0];
                const lastEl = focusables[focusables.length - 1];

                if (e.shiftKey && document.activeElement === firstEl) {
                    e.preventDefault();
                    lastEl.focus();
                } else if (!e.shiftKey && document.activeElement === lastEl) {
                    e.preventDefault();
                    firstEl.focus();
                }
            }
        });
    }

    /**
     * Waste monitoring dashboard subtle indicators
     */
    function initDashboardMicroInteractions() {
        const mapNodes = document.querySelectorAll(".monitor-node");
        mapNodes.forEach(node => {
            node.addEventListener("mouseenter", () => {
                node.style.transform = "scale(1.2)";
            });
            node.addEventListener("mouseleave", () => {
                node.style.transform = "scale(1)";
            });
        });
    }
})();

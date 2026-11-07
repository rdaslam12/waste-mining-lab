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
    });

    /**
     * Scroll-triggered reveals using IntersectionObserver
     */
    function initScrollReveals() {
        if (prefersReducedMotion) return;

        const revealElements = document.querySelectorAll(
            ".wml-editorial h1, .wml-editorial .lead, .wml-editorial .section-heading, " +
            ".wml-editorial .featured-publications, .wml-editorial .research-area, " +
            ".wml-editorial .project-feature, .wml-editorial .director-profile, " +
            ".wml-editorial .member-profile, .wml-editorial .activity-entry, " +
            ".wml-editorial .news-feature, .wml-editorial .news-card, " +
            ".wml-editorial .monitoring-platform, .wml-editorial .contact-layout, " +
            ".wml-editorial .editorial-cta"
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
                rootMargin: "0px 0px -60px 0px",
                threshold: 0.1
            }
        );

        revealElements.forEach(el => {
            el.classList.add("wml-reveal");
            observer.observe(el);
        });

        // Also stagger containers
        const staggerContainers = document.querySelectorAll(
            ".wml-editorial .research-areas, .wml-editorial .member-grid, " +
            ".wml-editorial .news-grid, .wml-editorial .journal-topics ul"
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
            // Shortcut: press '/' to focus search input when not already typing
            document.addEventListener("keydown", (e) => {
                if (e.key === "/" && document.activeElement !== searchInput && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
                    e.preventDefault();
                    searchInput.focus();
                }
            });
        }
    }

    /**
     * Waste monitoring dashboard subtle indicators
     */
    function initDashboardMicroInteractions() {
        const statusEl = document.querySelector(".data-status");
        if (!statusEl) return;

        // Interactive node points on the dashboard map if available
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

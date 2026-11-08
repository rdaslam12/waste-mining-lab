/**
 * Waste Mining Lab — Editorial Section Interactions & Motion Engine
 * Lightweight, 60fps, Zero-dependency, Prefers-reduced-motion respectful
 */

(function () {
    "use strict";

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    document.addEventListener("DOMContentLoaded", () => {
        initScrollReveals();
        initPublicationLiveSearch();
        initHorizontalSliders();
        initAlumniToggle();
        initProfileModals();
        initDashboardMicroInteractions();
    });

    /**
     * Scroll-triggered reveals using IntersectionObserver
     */
    function initScrollReveals() {
        if (prefersReducedMotion) return;

        const revealElements = document.querySelectorAll(
            ".wml-editorial h1, .wml-editorial .section-heading, " +
            ".wml-editorial .research-area-item, .wml-editorial .director-spotlight-card, " +
            ".wml-editorial .ra-card, .wml-editorial .contributor-card, " +
            ".wml-editorial .activity-entry, .wml-editorial .news-feature, " +
            ".wml-editorial .news-card, .wml-editorial .monitoring-platform, " +
            ".wml-editorial .contact-layout, .wml-editorial .grant-compact-item"
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
                rootMargin: "0px 0px -40px 0px",
                threshold: 0.05
            }
        );

        revealElements.forEach(el => {
            el.classList.add("wml-reveal");
            observer.observe(el);
        });
    }

    /**
     * Live search for publications with debouncing, aborting, and history support
     */
    function initPublicationLiveSearch() {
        const form = document.querySelector(".publication-filters");
        const searchInput = document.getElementById("publication-search");
        const yearSelect = document.getElementById("publication-year");
        const typeSelect = document.getElementById("publication-type");
        const resultsContainer = document.getElementById("publication-results");
        const statusIndicator = document.getElementById("publication-search-status");

        if (!form || !searchInput || !resultsContainer) return;

        let debounceTimer = null;
        let activeController = null;

        function performSearch(pushHistory) {
            if (activeController) {
                activeController.abort();
            }
            activeController = new AbortController();

            const formData = new FormData(form);
            const params = new URLSearchParams();
            for (const [key, value] of formData.entries()) {
                if (value.trim()) {
                    params.set(key, value.trim());
                }
            }

            const currentPath = form.getAttribute("action") || window.location.pathname;
            const queryUrl = params.toString() ? `${currentPath}?${params.toString()}` : currentPath;

            if (pushHistory) {
                window.history.pushState({ searchUrl: queryUrl }, "", queryUrl);
            }

            resultsContainer.classList.add("is-loading");
            if (statusIndicator) statusIndicator.textContent = "Updating publications...";

            fetch(queryUrl, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "text/html"
                },
                signal: activeController.signal
            })
            .then(res => {
                if (!res.ok) throw new Error("Search response error");
                return res.text();
            })
            .then(html => {
                let content = html;
                if (html.includes('id="publication-results"')) {
                    const temp = document.createElement("div");
                    temp.innerHTML = html;
                    const parsed = temp.querySelector("#publication-results");
                    if (parsed) content = parsed.innerHTML;
                }
                resultsContainer.innerHTML = content;
                resultsContainer.classList.remove("is-loading");
                if (statusIndicator) statusIndicator.textContent = "";

                updateClearLink(params.toString());
            })
            .catch(err => {
                if (err.name === "AbortError") return;
                resultsContainer.classList.remove("is-loading");
                if (statusIndicator) statusIndicator.textContent = "";
            });
        }

        function updateClearLink(queryString) {
            let clearLink = form.querySelector(".reset-link");
            const basePath = form.getAttribute("action") || window.location.pathname;
            if (queryString) {
                if (!clearLink) {
                    clearLink = document.createElement("a");
                    clearLink.className = "reset-link";
                    clearLink.textContent = "Clear filters";
                    clearLink.href = basePath;
                    form.appendChild(clearLink);
                }
            } else if (clearLink) {
                clearLink.remove();
            }
        }

        // Typing listener with ~280ms debounce
        searchInput.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                performSearch(true);
            }, 280);
        });

        // Fast shortcut key "/" to focus search input
        document.addEventListener("keydown", (e) => {
            if (e.key === "/" && document.activeElement !== searchInput && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
                e.preventDefault();
                searchInput.focus();
            }
        });

        // Instant filter on select changes
        if (yearSelect) {
            yearSelect.addEventListener("change", () => performSearch(true));
        }
        if (typeSelect) {
            typeSelect.addEventListener("change", () => performSearch(true));
        }

        // Form submit
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            clearTimeout(debounceTimer);
            performSearch(true);
        });

        // Intercept clicks on pagination and reset links within publication results/form
        document.addEventListener("click", (e) => {
            const resetLink = e.target.closest(".publication-filters .reset-link, #publication-results .reset-link");
            if (resetLink) {
                e.preventDefault();
                searchInput.value = "";
                if (yearSelect) yearSelect.value = "";
                if (typeSelect) typeSelect.value = "";
                performSearch(true);
                return;
            }

            const pageLink = e.target.closest("#publication-results .archive-pagination a");
            if (pageLink) {
                e.preventDefault();
                const targetUrl = pageLink.getAttribute("href");
                if (!targetUrl) return;

                if (activeController) activeController.abort();
                activeController = new AbortController();

                window.history.pushState({ searchUrl: targetUrl }, "", targetUrl);
                resultsContainer.classList.add("is-loading");

                fetch(targetUrl, {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "text/html"
                    },
                    signal: activeController.signal
                })
                .then(res => res.text())
                .then(html => {
                    let content = html;
                    if (html.includes('id="publication-results"')) {
                        const temp = document.createElement("div");
                        temp.innerHTML = html;
                        const parsed = temp.querySelector("#publication-results");
                        if (parsed) content = parsed.innerHTML;
                    }
                    resultsContainer.innerHTML = content;
                    resultsContainer.classList.remove("is-loading");
                })
                .catch(err => {
                    if (err.name === "AbortError") return;
                    resultsContainer.classList.remove("is-loading");
                });
            }
        });

        // Support browser Back/Forward navigation
        window.addEventListener("popstate", (e) => {
            const url = (e.state && e.state.searchUrl) ? e.state.searchUrl : window.location.href;
            const currentParams = new URLSearchParams(window.location.search);
            searchInput.value = currentParams.get("q") || "";
            if (yearSelect) yearSelect.value = currentParams.get("year") || "";
            if (typeSelect) typeSelect.value = currentParams.get("type") || "";

            if (activeController) activeController.abort();
            activeController = new AbortController();

            resultsContainer.classList.add("is-loading");
            fetch(url, {
                headers: { "X-Requested-With": "XMLHttpRequest", "Accept": "text/html" },
                signal: activeController.signal
            })
            .then(res => res.text())
            .then(html => {
                let content = html;
                if (html.includes('id="publication-results"')) {
                    const temp = document.createElement("div");
                    temp.innerHTML = html;
                    const parsed = temp.querySelector("#publication-results");
                    if (parsed) content = parsed.innerHTML;
                }
                resultsContainer.innerHTML = content;
                resultsContainer.classList.remove("is-loading");
                updateClearLink(currentParams.toString());
            })
            .catch(err => {
                if (err.name === "AbortError") return;
                resultsContainer.classList.remove("is-loading");
            });
        });
    }

    /**
     * Accessible horizontal sliders for Research Projects and Other Contributors
     */
    function initHorizontalSliders() {
        const sliders = document.querySelectorAll(".projects-slider, .contributors-slider");
        sliders.forEach(slider => {
            slider.addEventListener("keydown", (e) => {
                if (e.key === "ArrowRight") {
                    e.preventDefault();
                    slider.scrollBy({ left: 280, behavior: "smooth" });
                } else if (e.key === "ArrowLeft") {
                    e.preventDefault();
                    slider.scrollBy({ left: -280, behavior: "smooth" });
                }
            });
        });
    }

    /**
     * Alumni Section Toggle (Show Alumni / Hide Alumni)
     */
    function initAlumniToggle() {
        const toggleBtn = document.getElementById("alumni-toggle-btn");
        const alumniSection = document.getElementById("team-alumni-section");
        if (!toggleBtn || !alumniSection) return;

        toggleBtn.addEventListener("click", () => {
            const isExpanded = toggleBtn.getAttribute("aria-expanded") === "true";
            const nextState = !isExpanded;

            toggleBtn.setAttribute("aria-expanded", nextState ? "true" : "false");
            toggleBtn.textContent = nextState ? "Hide Alumni" : "Show Alumni";

            if (nextState) {
                alumniSection.removeAttribute("hidden");
                requestAnimationFrame(() => {
                    alumniSection.classList.add("is-expanded");
                });
            } else {
                alumniSection.classList.remove("is-expanded");
                setTimeout(() => {
                    if (toggleBtn.getAttribute("aria-expanded") === "false") {
                        alumniSection.setAttribute("hidden", "");
                    }
                }, 280);
            }
        });
    }

    /**
     * Accessible Profile Modals for Academic Team Members
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

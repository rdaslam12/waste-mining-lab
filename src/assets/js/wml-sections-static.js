/** Static archive interactions for the Cloudflare Pages build. */
(function () {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.addEventListener("DOMContentLoaded", () => {
    initScrollReveals();
    initPublicationArchive();
    initNewsFilters();
    initBibtexCopy();
    initHorizontalSliders();
    initAlumniToggle();
    initDashboardMicroInteractions();
  });

  function initScrollReveals() {
    if (reducedMotion) return;
    const elements = document.querySelectorAll(
      ".wml-editorial h1, .wml-editorial .section-heading, .wml-editorial .research-area-item, " +
      ".wml-editorial .director-spotlight-card, .wml-editorial .ra-card, .wml-editorial .contributor-card, " +
      ".wml-editorial .activity-entry, .wml-editorial .news-feature, .wml-editorial .news-card, " +
      ".wml-editorial .monitoring-platform, .wml-editorial .contact-layout, .wml-editorial .grant-compact-item"
    );
    if (!("IntersectionObserver" in window)) {
      elements.forEach((element) => element.classList.add("is-revealed"));
      return;
    }
    const observer = new IntersectionObserver((entries, currentObserver) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-revealed");
        currentObserver.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -40px 0px", threshold: 0.05 });
    elements.forEach((element) => {
      element.classList.add("wml-reveal");
      observer.observe(element);
    });
  }

  function initPublicationArchive() {
    const archive = document.querySelector("[data-publication-archive]");
    if (!archive) return;
    const form = archive.querySelector(".publication-filters");
    const search = archive.querySelector("#publication-search");
    const year = archive.querySelector("#publication-year");
    const type = archive.querySelector("#publication-type");
    const clear = archive.querySelector("[data-clear-publications]");
    const status = archive.querySelector("#publication-search-status");
    const empty = archive.querySelector("[data-publication-empty]");
    const pagination = archive.querySelector("[data-publication-pagination]");
    const previous = archive.querySelector("[data-page-previous]");
    const next = archive.querySelector("[data-page-next]");
    const pageStatus = archive.querySelector("[data-page-status]");
    const records = Array.from(archive.querySelectorAll("[data-publication]"));
    const groups = Array.from(archive.querySelectorAll("[data-publication-year-group]"));
    const pageSize = Number(archive.dataset.pageSize) || 12;
    let page = 1;

    function syncFromUrl() {
      const params = new URLSearchParams(window.location.search);
      search.value = params.get("q") || "";
      year.value = params.get("year") || "";
      type.value = params.get("type") || "";
      page = Math.max(1, Number(params.get("page")) || 1);
    }

    function updateUrl() {
      const params = new URLSearchParams();
      if (search.value.trim()) params.set("q", search.value.trim());
      if (year.value) params.set("year", year.value);
      if (type.value) params.set("type", type.value);
      if (page > 1) params.set("page", String(page));
      const query = params.toString();
      window.history.replaceState({}, "", `${window.location.pathname}${query ? `?${query}` : ""}${window.location.hash}`);
    }

    function render(resetPage) {
      if (resetPage) page = 1;
      const query = search.value.trim().toLocaleLowerCase();
      const matches = records.filter((record) => {
        const matchesText = !query || record.dataset.search.toLocaleLowerCase().includes(query);
        const matchesYear = !year.value || record.dataset.year === year.value;
        const matchesType = !type.value || record.dataset.type === type.value;
        return matchesText && matchesYear && matchesType;
      });
      const pages = Math.max(1, Math.ceil(matches.length / pageSize));
      page = Math.min(page, pages);
      const visible = new Set(matches.slice((page - 1) * pageSize, page * pageSize));
      records.forEach((record) => { record.hidden = !visible.has(record); });
      groups.forEach((group) => { group.hidden = !group.querySelector("[data-publication]:not([hidden])"); });
      empty.hidden = matches.length !== 0;
      pagination.hidden = matches.length <= pageSize;
      previous.disabled = page <= 1;
      next.disabled = page >= pages;
      pageStatus.textContent = `Page ${page} of ${pages}`;
      clear.hidden = !(query || year.value || type.value);
      status.textContent = matches.length === 1 ? "1 publication found." : `${matches.length} publications found.`;
      updateUrl();
    }

    let debounce;
    form.addEventListener("submit", (event) => { event.preventDefault(); render(true); });
    search.addEventListener("input", () => { window.clearTimeout(debounce); debounce = window.setTimeout(() => render(true), 200); });
    year.addEventListener("change", () => render(true));
    type.addEventListener("change", () => render(true));
    clear.addEventListener("click", () => { search.value = ""; year.value = ""; type.value = ""; render(true); search.focus(); });
    previous.addEventListener("click", () => { page -= 1; render(false); archive.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" }); });
    next.addEventListener("click", () => { page += 1; render(false); archive.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth" }); });
    document.addEventListener("keydown", (event) => {
      if (event.key === "/" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
        event.preventDefault();
        search.focus();
      }
    });
    window.addEventListener("popstate", () => { syncFromUrl(); render(false); });
    syncFromUrl();
    render(false);
  }

  function initNewsFilters() {
    const form = document.querySelector("[data-news-filters]");
    if (!form) return;
    const select = form.querySelector("#news-category");
    const clear = form.querySelector("[data-clear-news]");
    const cards = Array.from(document.querySelectorAll("[data-news-card]"));
    const empty = document.querySelector("[data-news-empty]");
    const featured = document.querySelector("[data-featured-news]");
    const disclosure = form.closest("details");
    const initial = new URLSearchParams(window.location.search).get("category") || "";
    select.value = Array.from(select.options).some((option) => option.value === initial) ? initial : "";
    if (disclosure && select.value) disclosure.open = true;
    function render() {
      let count = 0;
      cards.forEach((card) => {
        card.hidden = Boolean(select.value && card.dataset.category !== select.value);
        if (!card.hidden) count += 1;
      });
      if (featured) featured.hidden = Boolean(select.value);
      empty.hidden = count !== 0;
      clear.hidden = !select.value;
      const params = new URLSearchParams();
      if (select.value) params.set("category", select.value);
      window.history.replaceState({}, "", `${window.location.pathname}${params.toString() ? `?${params}` : ""}`);
    }
    form.addEventListener("submit", (event) => { event.preventDefault(); render(); });
    select.addEventListener("change", render);
    clear.addEventListener("click", () => { select.value = ""; render(); select.focus(); });
    render();
  }

  function initBibtexCopy() {
    document.addEventListener("click", async (event) => {
      const button = event.target.closest(".bibtex-copy-btn");
      if (!button) return;
      const original = button.textContent;
      try {
        await navigator.clipboard.writeText(button.dataset.bibtex || "");
        button.textContent = "Copied!";
      } catch {
        button.textContent = "Copy unavailable";
      }
      window.setTimeout(() => { button.textContent = original; }, 2000);
    });
  }

  function initHorizontalSliders() {
    document.querySelectorAll(".projects-slider, .contributors-slider").forEach((slider) => {
      slider.addEventListener("keydown", (event) => {
        if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
        event.preventDefault();
        slider.scrollBy({ left: event.key === "ArrowRight" ? 280 : -280, behavior: reducedMotion ? "auto" : "smooth" });
      });
    });
  }

  function initAlumniToggle() {
    const button = document.getElementById("alumni-toggle-btn");
    const section = document.getElementById("team-alumni-section");
    if (!button || !section) return;
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") !== "true";
      button.setAttribute("aria-expanded", String(expanded));
      button.textContent = expanded ? "Hide Alumni" : "Show Alumni";
      section.hidden = !expanded;
      section.classList.toggle("is-expanded", expanded);
    });
  }

  function initDashboardMicroInteractions() {
    document.querySelectorAll(".monitor-node").forEach((node) => {
      node.addEventListener("mouseenter", () => { node.style.transform = "scale(1.2)"; });
      node.addEventListener("mouseleave", () => { node.style.transform = "scale(1)"; });
    });
  }
})();

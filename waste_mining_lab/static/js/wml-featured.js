/* Homepage bento grid carousel, independent of navbar animation. */
(() => {
  const root = document.querySelector('[data-wml-featured]');
  if (!root) return;

  const story = root.querySelector('.wml-tile--story');
  const slides = Array.from(root.querySelectorAll('[data-wml-slide]'));
  const dots = Array.from(root.querySelectorAll('[data-wml-slide-to]'));
  const pauseButton = root.querySelector('[data-wml-pause]');
  if (!story || !slides.length || !pauseButton) return;

  let index = 0;
  let userPaused = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let hoverPaused = false;
  let focusPaused = false;
  let inView = true;

  function showSlide(nextIndex) {
    index = (nextIndex + slides.length) % slides.length;
    story.dataset.activeSlide = String(index);
    slides.forEach((slide, i) => {
      const active = i === index;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', String(!active));
    });
    dots.forEach((dot, i) => {
      const active = i === index;
      dot.classList.toggle('is-active', active);
      dot.setAttribute('aria-pressed', String(active));
    });
  }

  function updatePauseButton() {
    pauseButton.textContent = userPaused ? 'Play' : 'Pause';
    pauseButton.setAttribute('aria-pressed', String(userPaused));
    pauseButton.setAttribute('aria-label', userPaused ? 'Play automatic featured updates' : 'Pause automatic featured updates');
  }

  dots.forEach((button, i) => {
    button.addEventListener('click', () => showSlide(i));
  });
  pauseButton.addEventListener('click', () => {
    userPaused = !userPaused;
    updatePauseButton();
  });
  story.addEventListener('mouseenter', () => { hoverPaused = true; });
  story.addEventListener('mouseleave', () => { hoverPaused = false; });
  story.addEventListener('focusin', () => { focusPaused = true; });
  story.addEventListener('focusout', (event) => {
    focusPaused = story.contains(event.relatedTarget);
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      inView = entries[0].isIntersecting;
    }, { threshold: 0.2 });
    observer.observe(root);
  }

  window.setInterval(() => {
    if (!userPaused && !hoverPaused && !focusPaused && inView && !document.hidden) {
      showSlide(index + 1);
    }
  }, 5500);

  showSlide(0);
  updatePauseButton();
})();

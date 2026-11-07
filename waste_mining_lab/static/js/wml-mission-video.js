(() => {
    'use strict';

    const section = document.querySelector('.mission--video');
    if (!section) return;
    const video = section.querySelector('.mission__video');
    const toggle = section.querySelector('.mission__motion');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let nearby = false;
    let userPaused = false;
    let failed = false;
    let fadingOut = false;
    let fadeFrame = 0;
    let opacity = 0;
    let playPending = false;

    const canPlay = () => nearby && !document.hidden && !reducedMotion.matches && !userPaused && !failed;
    const stopFade = () => {
        cancelAnimationFrame(fadeFrame);
        fadeFrame = 0;
    };
    const setOpacity = value => {
        opacity = value;
        video.style.opacity = String(value);
    };
    const fade = (target, duration, done) => {
        stopFade();
        const startOpacity = opacity;
        const start = performance.now();
        const step = now => {
            const progress = Math.min(1, (now - start) / duration);
            setOpacity(startOpacity + (target - startOpacity) * progress);
            if (progress < 1) fadeFrame = requestAnimationFrame(step);
            else {
                fadeFrame = 0;
                if (done) done();
            }
        };
        fadeFrame = requestAnimationFrame(step);
    };

    const fallback = () => {
        failed = true;
        stopFade();
        video.pause();
        setOpacity(0);
        toggle.hidden = true;
    };
    const play = async () => {
        if (!canPlay() || playPending || !video.dataset.src) return;
        playPending = true;
        if (!video.hasAttribute('src')) {
            video.muted = true;
            video.src = video.dataset.src;
        }
        try {
            await video.play();
            if (!canPlay()) video.pause();
        } catch (error) {
            // A visibility change may interrupt an outstanding play request.
            if (error.name !== 'AbortError') fallback();
        } finally {
            playPending = false;
        }
    };
    const syncPlayback = () => {
        if (canPlay()) play();
        else {
            stopFade();
            fadingOut = false;
            video.pause();
            if (reducedMotion.matches) setOpacity(0);
        }
    };
    const restart = () => {
        fadingOut = false;
        video.currentTime = 0;
        if (canPlay()) {
            if (video.paused) play();
            else fade(1, 250);
        }
    };
    const endFade = () => {
        if (fadingOut || !canPlay()) return;
        fadingOut = true;
        fade(0, 250, restart);
    };

    video.addEventListener('playing', () => {
        if (!canPlay()) { video.pause(); return; }
        toggle.hidden = false;
        if (!fadingOut) fade(1, 250);
    });
    video.addEventListener('timeupdate', () => {
        if (Number.isFinite(video.duration) && video.duration - video.currentTime <= 0.55) endFade();
    });
    // Native loop is deliberately absent: the fade owns the rewind.
    video.addEventListener('ended', endFade);
    video.addEventListener('error', fallback);
    toggle.addEventListener('click', () => {
        userPaused = !userPaused;
        toggle.textContent = userPaused ? 'Play background video' : 'Pause background video';
        syncPlayback();
    });
    document.addEventListener('visibilitychange', syncPlayback);
    reducedMotion.addEventListener('change', syncPlayback);

    if ('IntersectionObserver' in window) {
        const playbackObserver = new IntersectionObserver(entries => {
            nearby = entries[0].isIntersecting;
            syncPlayback();
        }, { rootMargin: '200px 0px' });
        playbackObserver.observe(section);
        const entranceObserver = new IntersectionObserver(entries => {
            if (!entries[0].isIntersecting) return;
            section.classList.add('is-visible');
            entranceObserver.disconnect();
        }, { threshold: 0.15 });
        entranceObserver.observe(section);
    }
    // Without IntersectionObserver the readable, static fallback remains.
})();

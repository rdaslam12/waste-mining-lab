/* Adapted from the supplied Solace fixed-grid halftone reference. */
(() => {
    'use strict';
    const section = document.querySelector('.mission--halftone');
    if (!section) return;
    const canvas = section.querySelector('.mission__canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const control = section.querySelector('.mission__motion');
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const finePointer = matchMedia('(hover: hover) and (pointer: fine)');
    const hash = (i, j) => {
        const h = Math.sin(i * 127.1 + j * 311.7) * 43758.5453;
        return h - Math.floor(h);
    };
    const mix = (a, b, t) => a.map((v, k) => Math.round(v + (b[k] - v) * t));
    const smooth = (a, b, value) => {
        const t = Math.max(0, Math.min(1, (value - a) / (b - a)));
        return t * t * (3 - 2 * t);
    };
    let width = 0, height = 0, step = 22, dots = [];
    let frame = 0, previous = 0, elapsed = 0, visible = false, paused = false;
    const pointer = { x: 0, y: 0, tx: 0, ty: 0, strength: 0, active: false };
    function draw(time, dt = 16) {
        ctx.clearRect(0, 0, width, height);
        const ease = 1 - Math.exp(-dt / 95);
        pointer.x += (pointer.tx - pointer.x) * ease;
        pointer.y += (pointer.ty - pointer.y) * ease;
        pointer.strength += ((pointer.active ? 1 : 0) - pointer.strength) * ease;
        for (const d of dots) {
            const wave = reduced.matches ? 0.7 : 0.5 + 0.5 * Math.sin(time * (0.65 + d.b * 1.1) + d.a * 6.283 + Math.sin(time * 0.35 + d.i * 0.21 + d.j * 0.13) * 1.4);
            const distance = (d.x - pointer.x) ** 2 + (d.y - pointer.y) ** 2;
            const hover = reduced.matches ? 0 : Math.exp(-distance / (step * step * 22)) * pointer.strength;
            const radius = step * 0.36 * Math.min(1.08, (0.42 + 0.58 * wave ** 1.3) * d.size + hover * 0.48);
            
            ctx.globalAlpha = d.alpha * 0.5;
            ctx.fillStyle = d.color;

            const x = d.x;
            const y = d.y;
            const r = radius;

            // Small pine-tree silhouette
            ctx.beginPath();
            ctx.moveTo(x, y - r * 1.5);
            ctx.lineTo(x - r * 0.7, y - r * 0.1);
            ctx.lineTo(x - r * 0.35, y - r * 0.1);
            ctx.lineTo(x - r, y + r * 0.85);
            ctx.lineTo(x + r, y + r * 0.85);
            ctx.lineTo(x + r * 0.35, y - r * 0.1);
            ctx.lineTo(x + r * 0.7, y - r * 0.1);
            ctx.closePath();
            ctx.fill();

            // Tree trunk
            ctx.fillRect(
                x - r * 0.14,
                y + r * 0.8,
                r * 0.28,
                r * 0.45
            );

        }
        ctx.globalAlpha = 1;
    }
    function tick(now) {
        frame = 0;
        const dt = previous ? Math.min(now - previous, 50) : 16;
        previous = now;
        elapsed += dt / 1000;
        draw(elapsed, dt);
        frame = requestAnimationFrame(tick);
    }
    function sync() {
        cancelAnimationFrame(frame);
        frame = 0;
        previous = 0;
        control.hidden = reduced.matches;
        if (visible && !document.hidden && !reduced.matches && !paused) frame = requestAnimationFrame(tick);
        else if (reduced.matches) draw(0);
    }
    function resize() {
        width = section.clientWidth;
        height = section.clientHeight;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const mobile = width < 680;
        const compact = width < 1024;
        step = mobile ? 25 : Math.max(20, Math.min(27, width / 64));
        dots = [];
        for (let j = 0; j * step < height; j++) {
            for (let i = 0; i * step < width; i++) {
                const x = i * step + step / 2, y = j * step + step / 2;
                const a = hash(i, j), b = hash(i + 71, j + 13), c = hash(i + 9, j + 97);
                const v = y / height;
                const density = smooth(0.03, 0.8, v);
                if (a > 0.05 + density * 0.95) continue;
                // Text stays quiet; the field opens to the right and below it.
                const open = compact ? smooth(0.78, 1, v) : Math.max(smooth(0.48, 0.82, x / width), smooth(0.78, 1, v));
                const color = c > 0.975 ? [226, 241, 140] : v < 0.6
                    ? mix([11, 75, 49], c > 0.55 ? [54, 199, 130] : [31, 160, 132], v / 0.6)
                    : mix([54, 199, 130], c > 0.55 ? [215, 233, 214] : [165, 230, 183], (v - 0.6) / 0.4);
                dots.push({ i, j, x, y, a, b, size: 0.5 + density * 0.5, alpha: (mobile ? 0.035 : 0.045) + open * (mobile ? 0.48 : 0.8), color: `rgb(${color.join(',')})` });
            }
        }
        draw(reduced.matches ? 0 : elapsed);
    }
    section.addEventListener('pointermove', event => {
        if (!finePointer.matches || reduced.matches || paused) return;
        const rect = section.getBoundingClientRect();
        pointer.tx = event.clientX - rect.left;
        pointer.ty = event.clientY - rect.top;
        if (!pointer.active) { pointer.x = pointer.tx; pointer.y = pointer.ty; }
        pointer.active = true;
    }, { passive: true });
    section.addEventListener('pointerleave', () => { pointer.active = false; });
    // Scrolling under a stationary pointer must not leave a false hover hotspot.
    window.addEventListener('scroll', () => { pointer.active = false; }, { passive: true });
    control.addEventListener('click', () => {
        paused = !paused;
        pointer.active = false;
        control.setAttribute('aria-pressed', String(paused));
        control.textContent = paused ? 'Resume dot animation' : 'Pause dot animation';
        sync();
    });
    new ResizeObserver(resize).observe(section);
    new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting;
        sync();
    }).observe(section);
    reduced.addEventListener('change', sync);
    document.addEventListener('visibilitychange', sync);
    resize();
})();

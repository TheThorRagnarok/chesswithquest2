/* Tomáš Zikmund · site behaviour
   One smooth-scroll engine (Lenis) driving GSAP ScrollTrigger. Everything motion-related
   sits behind prefers-reduced-motion; menu, nav material and email copy work without it. */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduceMQ = window.matchMedia('(prefers-reduced-motion: reduce)');
  var hasGsap = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';
  var lenis = null;

  /* ---------- Nav material on scroll ---------- */
  var nav = document.querySelector('[data-nav]');
  function onScroll() { nav.classList.toggle('is-scrolled', window.scrollY > 24); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile menu sheet ---------- */
  var menuBtn = document.querySelector('[data-menu-btn]');
  var menu = document.querySelector('[data-menu]');
  var menuTimer;
  function setMenu(open) {
    clearTimeout(menuTimer);
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.querySelector('.menu-btn-label').textContent = open ? 'Close' : 'Menu';
    if (open) {
      menu.hidden = false;
      requestAnimationFrame(function () {
        menu.classList.add('is-open');
        var first = menu.querySelector('a');
        if (first) first.focus({ preventScroll: true });
      });
      if (lenis) lenis.stop();
      document.body.style.overflow = 'hidden';
    } else {
      menu.classList.remove('is-open');
      menuTimer = setTimeout(function () { menu.hidden = true; }, 260);
      if (lenis) lenis.start();
      document.body.style.overflow = '';
    }
  }
  menuBtn.addEventListener('click', function () {
    setMenu(menuBtn.getAttribute('aria-expanded') !== 'true');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menuBtn.getAttribute('aria-expanded') === 'true') {
      setMenu(false);
      menuBtn.focus();
    }
  });
  window.matchMedia('(min-width: 821px)').addEventListener('change', function (e) {
    if (e.matches && menuBtn.getAttribute('aria-expanded') === 'true') setMenu(false);
  });

  /* ---------- In-page anchors (Lenis-aware, moves focus for keyboard users) ---------- */
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href^="#"]');
    if (!a) return;
    var id = a.getAttribute('href');
    var target = id === '#top' || id === '#' ? document.body : document.querySelector(id);
    if (!target) return;
    e.preventDefault();
    if (menuBtn.getAttribute('aria-expanded') === 'true') setMenu(false);
    var focusEl = target === document.body ? document.querySelector('#main') : target;
    if (lenis) {
      lenis.scrollTo(target === document.body ? 0 : target, { offset: 0, duration: 1.2 });
    } else if (target === document.body) {
      window.scrollTo({ top: 0, behavior: reduceMQ.matches ? 'auto' : 'smooth' });
    } else {
      target.scrollIntoView({ behavior: reduceMQ.matches ? 'auto' : 'smooth' });
    }
    if (focusEl) {
      if (!focusEl.hasAttribute('tabindex')) focusEl.setAttribute('tabindex', '-1');
      focusEl.focus({ preventScroll: true });
    }
    history.replaceState(null, '', id === '#top' ? location.pathname + location.search : id);
  });

  /* ---------- Copy email ---------- */
  var copyBtn = document.querySelector('[data-copy]');
  var copyStatus = document.querySelector('[data-copy-status]');
  var copyTimer;
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      var email = copyBtn.getAttribute('data-email');
      var done = function (msg) {
        copyStatus.textContent = msg;
        clearTimeout(copyTimer);
        copyTimer = setTimeout(function () { copyStatus.textContent = ''; }, 2600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(email).then(
          function () { done('Copied. Talk soon.'); },
          function () { done('Could not copy. The address is ' + email); }
        );
      } else {
        done('The address is ' + email);
      }
    });
  }

  /* ---------- Motion ---------- */
  if (!hasGsap) { root.classList.remove('motion'); return; }
  window.__tzStarted = true;

  var gsap = window.gsap;
  var ScrollTrigger = window.ScrollTrigger;
  gsap.registerPlugin(ScrollTrigger);

  /* Split helpers. The readable sentence lives in a visually-hidden span;
     the animated words are aria-hidden so screen readers get one clean string. */
  function splitWords(el, masked) {
    var text = el.textContent.trim().replace(/\s+/g, ' ');
    var words = text.split(' ');
    var html = '<span class="visually-hidden">' + text + '</span><span aria-hidden="true">';
    words.forEach(function (w, i) {
      var inner = '<span class="w">' + w + '</span>';
      html += (masked ? '<span class="wm">' + inner + '</span>' : inner) + (i < words.length - 1 ? ' ' : '');
    });
    el.innerHTML = html + '</span>';
    return el.querySelectorAll('.w');
  }

  var mm = gsap.matchMedia();

  mm.add('(prefers-reduced-motion: no-preference)', function () {
    /* Lenis smooth scroll, driven by GSAP's ticker so ScrollTrigger stays in sync */
    if (typeof window.Lenis !== 'undefined') {
      lenis = new window.Lenis({ lerp: 0.11, wheelMultiplier: 1, smoothWheel: true });
      lenis.on('scroll', ScrollTrigger.update);
      var raf = function (t) { lenis.raf(t * 1000); };
      gsap.ticker.add(raf);
      gsap.ticker.lagSmoothing(0);
    }

    /* Hero intro: red panel sweeps in, retracts to reveal the frame, name rises */
    var media = document.querySelector('[data-hero-media]');
    var wipe = document.querySelector('[data-hero-wipe]');
    var img = document.querySelector('[data-hero-img]');
    gsap.set(wipe, { scaleX: 1, transformOrigin: 'right center' });

    var tl = gsap.timeline({ defaults: { ease: 'expo.out' }, delay: 0.1 });
    tl.to(media, { clipPath: 'inset(0 0% 0 0)', duration: 0.9, ease: 'expo.inOut' }, 0)
      .to(wipe, { scaleX: 0, duration: 0.9, ease: 'expo.inOut' }, 0.62)
      .to(img, { scale: 1, duration: 1.8 }, 0.62)
      .to('.hero-title .line > span', { y: 0, duration: 1.2, stagger: 0.09 }, 0.55)
      .to('[data-hero-meta]', { opacity: 1, duration: 0.8 }, 0.9)
      .fromTo('[data-hero-fade]', { y: 16 }, { opacity: 1, y: 0, duration: 0.9, stagger: 0.08 }, 1.0)
      .to('.nav', { opacity: 1, duration: 0.8 }, 1.0);

    /* Pointer parallax on the hero frame (fine pointers only, returns home on leave/blur) */
    var hero = document.querySelector('.hero');
    var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    var xTo, yTo, onMove, onLeave;
    if (fine) {
      xTo = gsap.quickTo(img, 'x', { duration: 0.9, ease: 'power3.out' });
      yTo = gsap.quickTo(img, 'y', { duration: 0.9, ease: 'power3.out' });
      var pending = false, px = 0, py = 0;
      onMove = function (e) {
        px = e.clientX; py = e.clientY;
        if (pending) return;
        pending = true;
        requestAnimationFrame(function () {
          pending = false;
          var r = hero.getBoundingClientRect();
          xTo(((px - r.left) / r.width - 0.5) * -18);
          yTo(((py - r.top) / r.height - 0.5) * -12);
        });
      };
      onLeave = function () { xTo(0); yTo(0); };
      hero.addEventListener('pointermove', onMove);
      hero.addEventListener('pointerleave', onLeave);
      window.addEventListener('blur', onLeave);
    }

    /* Hero frame drifts slower than the page as it leaves */
    gsap.to(img, {
      yPercent: 8, ease: 'none',
      scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true }
    });

    /* Section headings: word-by-word rise */
    document.querySelectorAll('[data-split]').forEach(function (el) {
      var words = splitWords(el, true);
      gsap.set(words, { yPercent: 110 });
      gsap.to(words, {
        yPercent: 0, duration: 1.1, ease: 'expo.out', stagger: 0.06,
        scrollTrigger: { trigger: el, start: 'top 82%', once: true }
      });
    });

    /* Manifesto: words light up as you read */
    var manifesto = document.querySelector('[data-scrub-words]');
    if (manifesto) {
      var mw = splitWords(manifesto, false);
      gsap.to(mw, {
        opacity: 1, ease: 'none', stagger: 0.1,
        scrollTrigger: { trigger: manifesto, start: 'top 78%', end: 'bottom 42%', scrub: 0.4 }
      });
    }

    /* Generic reveals */
    ScrollTrigger.batch('[data-reveal]', {
      start: 'top 88%', once: true,
      onEnter: function (batch) {
        gsap.to(batch, { opacity: 1, y: 0, duration: 0.9, ease: 'expo.out', stagger: 0.08 });
      }
    });

    /* Process: the clock line runs across three periods, each 20:00 counts down as it passes */
    var clockLine = document.querySelector('[data-clock-line]');
    var times = document.querySelectorAll('.period-time');
    var fmt = function (s) {
      var m = Math.floor(s / 60), r = Math.floor(s % 60);
      return (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r;
    };
    gsap.to(clockLine, {
      scaleX: 1, ease: 'none',
      scrollTrigger: {
        trigger: '[data-process]', start: 'top 65%', end: 'bottom 75%', scrub: 0.3,
        onUpdate: function (self) {
          var p = self.progress * 3;
          times.forEach(function (t, i) {
            var local = Math.min(1, Math.max(0, p - i));
            t.textContent = fmt(1200 * (1 - local));
          });
        }
      }
    });

    /* Contact: the outlined 12 slides against the scroll */
    gsap.fromTo('[data-contact-12]', { xPercent: 10 }, {
      xPercent: -14, ease: 'none',
      scrollTrigger: { trigger: '[data-contact]', start: 'top bottom', end: 'bottom top', scrub: true }
    });

    /* Phone story bars only animate while the work section is on screen */
    ScrollTrigger.create({
      trigger: '[data-work]', start: 'top bottom', end: 'bottom top',
      toggleClass: { targets: '[data-work]', className: 'is-playing' }
    });

    return function () {
      if (lenis) { lenis.destroy(); lenis = null; }
      if (fine && hero) {
        hero.removeEventListener('pointermove', onMove);
        hero.removeEventListener('pointerleave', onLeave);
        window.removeEventListener('blur', onLeave);
      }
    };
  });

  /* Work: pinned horizontal run on wide screens only */
  mm.add('(min-width: 900px) and (prefers-reduced-motion: no-preference)', function () {
    var work = document.querySelector('[data-work]');
    var track = document.querySelector('[data-work-track]');
    var bar = document.querySelector('[data-work-progress]');
    work.classList.add('is-pinned');
    var dist = function () { return Math.max(0, track.scrollWidth - window.innerWidth); };
    gsap.to(track, {
      x: function () { return -dist(); },
      ease: 'none',
      scrollTrigger: {
        trigger: work, start: 'top top',
        end: function () { return '+=' + dist(); },
        pin: true, scrub: 0.6, invalidateOnRefresh: true, anticipatePin: 1,
        onUpdate: function (self) { gsap.set(bar, { scaleX: self.progress }); }
      }
    });
    return function () { work.classList.remove('is-pinned'); };
  });

  /* Reduced motion: final states, no smooth scroll, no scrubbing */
  mm.add('(prefers-reduced-motion: reduce)', function () {
    root.classList.remove('motion');
  });

  /* Measurements change once webfonts and images land */
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
  window.addEventListener('load', function () { ScrollTrigger.refresh(); });
})();

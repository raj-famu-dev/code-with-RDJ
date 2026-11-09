/* ============================================================
   RDJ-Portfolio — app.js
   Boot sequence, constellation field, scramble text, letter reveal,
   scroll reveals, counters, card tilt, magnetic buttons,
   timeline scrub, custom cursor, nav behavior.
   All effects respect prefers-reduced-motion.
   ============================================================ */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  /* ---------- Boot preloader ---------- */
  var preloader = document.querySelector('.preloader');
  var nameEl = document.querySelector('.hero-name');

  // Split hero name into letters
  document.querySelectorAll('[data-split]').forEach(function (line) {
    var text = line.textContent;
    line.textContent = '';
    for (var i = 0; i < text.length; i++) {
      var s = document.createElement('span');
      s.className = 'ch';
      s.textContent = text[i];
      s.style.transitionDelay = (i * 55) + 'ms';
      line.appendChild(s);
    }
  });

  function endBoot() {
    if (preloader) {
      preloader.classList.add('done');
      setTimeout(function () { preloader.remove(); }, 800);
    }
    if (nameEl) nameEl.classList.add('played');
    document.body.classList.remove('locked');
  }

  if (reduced || !preloader) {
    endBoot();
  } else {
    document.body.classList.add('locked');
    var lines = [
      'raj@famu:~$ whoami',
      'raj-famu-dev · cs undergrad · famu',
      'raj@famu:~$ make evidence',
      'compiling portfolio … ok'
    ];
    var out = preloader.querySelector('.preloader-lines');
    var li = 0;
    preloader.classList.add('loading');
    (function typeLine() {
      if (li < lines.length) {
        out.textContent += lines[li] + '\n';
        li++;
        setTimeout(typeLine, 260);
      } else {
        setTimeout(endBoot, 420);
      }
    })();
  }

  /* ---------- Custom cursor ---------- */
  if (finePointer && !reduced) {
    var dot = document.querySelector('.cursor-dot');
    var ring = document.querySelector('.cursor-ring');
    var mx = -100, my = -100, rx = -100, ry = -100;
    document.addEventListener('pointermove', function (e) {
      mx = e.clientX; my = e.clientY;
      if (dot) dot.style.transform = 'translate(' + (mx - 3) + 'px,' + (my - 3) + 'px)';
    });
    (function loop() {
      rx += (mx - rx) * 0.18;
      ry += (my - ry) * 0.18;
      if (ring) {
        var half = ring.offsetWidth / 2;
        ring.style.transform = 'translate(' + (rx - half) + 'px,' + (ry - half) + 'px)';
      }
      requestAnimationFrame(loop);
    })();
    document.querySelectorAll('a, button, [data-cursor]').forEach(function (el) {
      el.addEventListener('pointerenter', function () { ring.classList.add('hover'); });
      el.addEventListener('pointerleave', function () { ring.classList.remove('hover'); });
    });
  }

  /* ---------- Hero constellation canvas ---------- */
  var canvas = document.querySelector('.constellation');
  if (canvas && !reduced) {
    var ctx = canvas.getContext('2d');
    var W, H, DPR = Math.min(window.devicePixelRatio || 1, 2);
    var particles = [];
    var COUNT = window.innerWidth < 720 ? 55 : 110;
    var mouse = { x: -9999, y: -9999 };

    function resize() {
      var r = canvas.parentElement.getBoundingClientRect();
      W = r.width; H = r.height;
      canvas.width = W * DPR; canvas.height = H * DPR;
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    }
    resize();
    window.addEventListener('resize', resize);

    for (var i = 0; i < COUNT; i++) {
      particles.push({
        x: Math.random() * 2000, y: Math.random() * 1200,
        vx: (Math.random() - 0.5) * 0.22,
        vy: (Math.random() - 0.5) * 0.22,
        r: Math.random() * 1.6 + 0.4,
        amber: Math.random() < 0.16
      });
    }

    canvas.parentElement.addEventListener('pointermove', function (e) {
      var r = canvas.getBoundingClientRect();
      mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
    });
    canvas.parentElement.addEventListener('pointerleave', function () {
      mouse.x = -9999; mouse.y = -9999;
    });

    (function draw() {
      ctx.clearRect(0, 0, W, H);
      var i, j, p, q, dx, dy, d;
      for (i = 0; i < particles.length; i++) {
        p = particles[i];
        // gentle mouse repulsion
        dx = p.x - mouse.x; dy = p.y - mouse.y;
        d = dx * dx + dy * dy;
        if (d < 26000) {
          var f = (1 - d / 26000) * 0.9;
          var m = Math.sqrt(d) || 1;
          p.x += (dx / m) * f; p.y += (dy / m) * f;
        }
        p.x += p.vx; p.y += p.vy;
        if (p.x < -20) p.x = W + 20; if (p.x > W + 20) p.x = -20;
        if (p.y < -20) p.y = H + 20; if (p.y > H + 20) p.y = -20;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.amber ? 'rgba(232,134,46,0.75)' : 'rgba(237,230,218,0.38)';
        ctx.fill();
      }
      // constellation links
      for (i = 0; i < particles.length; i++) {
        for (j = i + 1; j < particles.length; j++) {
          p = particles[i]; q = particles[j];
          dx = p.x - q.x; dy = p.y - q.y;
          d = dx * dx + dy * dy;
          if (d < 12500) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = 'rgba(237,230,218,' + (0.09 * (1 - d / 12500)) + ')';
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(draw);
    })();
  }

  /* ---------- Scramble text ---------- */
  var scrambleEl = document.querySelector('[data-scramble]');
  if (scrambleEl && !reduced) {
    var roles = [
      'computer science student',
      'future ai engineer',
      'java foundation → python',
      'building in public',
      'evidence over claims'
    ];
    var CHARS = 'abcdefghijklmnopqrstuvwxyz01<>/#';
    var ri = 0;
    function scrambleTo(word) {
      var frame = 0, total = 24;
      (function tick() {
        var done = '';
        for (var k = 0; k < word.length; k++) {
          if (k < (frame / total) * word.length) done += word[k];
          else done += CHARS[Math.floor(Math.random() * CHARS.length)];
        }
        scrambleEl.textContent = done;
        if (frame++ < total) requestAnimationFrame(tick);
      })();
    }
    scrambleTo(roles[0]);
    setInterval(function () {
      ri = (ri + 1) % roles.length;
      scrambleTo(roles[ri]);
    }, 3000);
  } else if (scrambleEl) {
    scrambleEl.textContent = 'computer science student';
  }

  /* ---------- Scroll reveals (opacity only, no CLS) ---------- */
  var revealEls = document.querySelectorAll('.reveal-el');
  if ('IntersectionObserver' in window && !reduced) {
    revealEls.forEach(function (el) { el.classList.add('is-hidden'); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.remove('is-hidden');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Counters ---------- */
  var counters = document.querySelectorAll('.counter');
  if (counters.length && 'IntersectionObserver' in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        cio.unobserve(entry.target);
        var el = entry.target;
        var target = parseInt(el.getAttribute('data-count'), 10) || 0;
        var suffix = el.getAttribute('data-suffix') || '';
        if (reduced) { el.textContent = target + suffix; return; }
        var start = null, dur = 1400;
        function stepFn(ts) {
          if (!start) start = ts;
          var t = Math.min((ts - start) / dur, 1);
          var eased = 1 - Math.pow(1 - t, 4);
          el.textContent = Math.round(target * eased) + suffix;
          if (t < 1) requestAnimationFrame(stepFn);
        }
        requestAnimationFrame(stepFn);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  } else {
    counters.forEach(function (el) {
      el.textContent = el.getAttribute('data-count') + (el.getAttribute('data-suffix') || '');
    });
  }

  /* ---------- Ledger card tilt ---------- */
  if (finePointer && !reduced) {
    document.querySelectorAll('[data-tilt]').forEach(function (card) {
      card.addEventListener('pointermove', function (e) {
        var r = card.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        card.style.transform = 'perspective(900px) rotateX(' + (-py * 4) + 'deg) rotateY(' + (px * 5) + 'deg)';
      });
      card.addEventListener('pointerleave', function () {
        card.style.transform = 'perspective(900px) rotateX(0) rotateY(0)';
      });
    });
  }

  /* ---------- Magnetic buttons ---------- */
  if (finePointer && !reduced) {
    document.querySelectorAll('.magnetic').forEach(function (btn) {
      btn.addEventListener('pointermove', function (e) {
        var r = btn.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.22;
        var y = (e.clientY - r.top - r.height / 2) * 0.32;
        btn.style.translate = x + 'px ' + y + 'px';
      });
      btn.addEventListener('pointerleave', function () {
        btn.style.translate = '0px 0px';
      });
    });
  }

  /* ---------- Timeline scrub ---------- */
  var timeline = document.getElementById('timeline');
  if (timeline) {
    var fill = timeline.querySelector('.timeline-fill');
    var items = timeline.querySelectorAll('.timeline-item');
    function scrub() {
      var r = timeline.getBoundingClientRect();
      var vh = window.innerHeight;
      var progress = Math.min(Math.max((vh * 0.75 - r.top) / r.height, 0), 1);
      if (fill) fill.style.height = (progress * 100) + '%';
      items.forEach(function (item) {
        var ir = item.getBoundingClientRect();
        item.classList.toggle('lit', ir.top < vh * 0.75);
      });
    }
    window.addEventListener('scroll', scrub, { passive: true });
    scrub();
  }

  /* ---------- Nav + scroll progress ---------- */
  var header = document.querySelector('.site-header');
  var progressBar = document.querySelector('.scroll-progress span');
  var lastY = window.scrollY;
  function onScroll() {
    var y = window.scrollY;
    if (header) {
      header.classList.toggle('scrolled', y > 24);
      if (y > lastY && y > 140) header.classList.add('hidden');
      else header.classList.remove('hidden');
    }
    if (progressBar) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      progressBar.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';
    }
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

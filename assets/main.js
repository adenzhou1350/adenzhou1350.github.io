/* ============================================================
   周栩丞 Aden — 交互脚本
   克制反馈：一次性淡入上移 + 1px 顶部进度线 + 顶栏收拢
   ============================================================ */
(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1. 一次性淡入上移 ---------- */
  (function reveal() {
    var targets = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
    if (!targets.length) return;

    function showAll() {
      targets.forEach(function (el) { el.classList.add('is-visible'); });
    }

    if (reducedMotion || !('IntersectionObserver' in window)) {
      showAll();
      return;
    }

    var revealed = 0;
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        revealed++;
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.05 });

    targets.forEach(function (el) { observer.observe(el); });

    // 兜底：观察器若因任何原因始终不触发，内容不能永久不可见
    setTimeout(function () {
      if (revealed > 0) return;
      showAll();
    }, 2500);
  })();

  /* ---------- 2. 顶部滚动进度（1px） ---------- */
  (function progress() {
    var bar = document.querySelector('.progress i');
    if (!bar) return;

    var ticking = false;

    function update() {
      var doc = document.documentElement;
      var max = doc.scrollHeight - doc.clientHeight;
      var ratio = max > 0 ? window.scrollY / max : 0;
      bar.style.width = (Math.min(1, Math.max(0, ratio)) * 100).toFixed(2) + '%';
      ticking = false;
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }

    if (!reducedMotion) {
      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll, { passive: true });
    }
    update();
  })();

  /* ---------- 3. 顶栏滚动后显形 ---------- */
  (function topbar() {
    var bar = document.querySelector('.topbar');
    if (!bar) return;

    var ticking = false;

    function update() {
      bar.classList.toggle('is-stuck', window.scrollY > 12);
      ticking = false;
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    update();
  })();

  /* ---------- 4. 开源数据（读 JSON，失败则保留页面里的静态值） ---------- */
  (function ossStats() {
    var root = document.getElementById('oss-stats');
    if (!root) return;

    fetch('oss-stats.json?t=' + Date.now(), { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d) return;

        var own = d.ownRepo && d.ownRepo.merged;
        var fields = {
          mergedTotal: d.mergedTotal,
          upstreamMerged: d.upstreamMerged,
          own: own,
          reviewedTotal: d.reviewedTotal
        };

        Object.keys(fields).forEach(function (k) {
          if (typeof fields[k] !== 'number') return;
          root.querySelectorAll('[data-oss="' + k + '"]').forEach(function (el) {
            el.textContent = fields[k];
          });
        });

        var stamp = document.getElementById('oss-stamp');
        if (stamp && d.generatedAt) {
          stamp.insertAdjacentHTML('afterbegin',
            '更新于 ' + d.generatedAt + ' · ');
        }
      })
      .catch(function () { /* 静默失败：页面里的静态值仍然正确 */ });
  })();
})();

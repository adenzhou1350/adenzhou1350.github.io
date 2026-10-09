(() => {
  'use strict';
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    const close = () => { nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); toggle.textContent = '菜单 +'; };
    toggle.addEventListener('click', () => { const open = nav.classList.toggle('is-open'); toggle.setAttribute('aria-expanded', String(open)); toggle.textContent = open ? '关闭 −' : '菜单 +'; });
    nav.addEventListener('click', (event) => { if (event.target.closest('a')) close(); });
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && nav.classList.contains('is-open')) { close(); toggle.focus(); } });
    window.matchMedia('(min-width: 781px)').addEventListener('change', (event) => { if (event.matches) close(); });
  }
  const list = document.querySelector('[data-content-list]');
  if (list) {
    const search = document.querySelector('[data-search]');
    const buttons = [...document.querySelectorAll('[data-filter]')];
    const items = [...list.querySelectorAll('[data-category]')];
    const status = document.querySelector('[data-results-status]');
    const empty = document.querySelector('[data-empty]');
    let category = '全部';
    const filter = () => {
      const query = search.value.trim().toLocaleLowerCase();
      let count = 0;
      for (const item of items) {
        const show = (category === '全部' || item.dataset.category === category) && item.dataset.search.toLocaleLowerCase().includes(query);
        item.hidden = !show; if (show) count++;
      }
      status.textContent = `显示 ${count} 篇文章`;
      empty.hidden = count !== 0;
    };
    buttons.forEach(button => button.addEventListener('click', () => {
      category = button.dataset.filter;
      buttons.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      filter();
    }));
    search.addEventListener('input', filter);
  }
  document.querySelectorAll('.copy-code').forEach(button => {
    button.addEventListener('click', async () => {
      const text = button.parentElement.querySelector('code').textContent;
      try { await navigator.clipboard.writeText(text); button.textContent = '已复制'; }
      catch { button.textContent = '请选中复制'; }
      window.setTimeout(() => { button.textContent = '复制'; }, 2000);
    });
  });
  const demo = document.querySelector('[data-cache-demo]');
  if (demo) {
    const states = ['save', 'cancel', 'confirm'];
    let current = 0, filename = 'screen.txt';
    const pathCache = new Map(), contentCache = new Map();
    const $ = selector => demo.querySelector(selector);
    const update = action => {
      const content = `button=${states[current]}`;
      const pathHit = pathCache.has(filename), contentHit = contentCache.has(content);
      if (!pathHit) pathCache.set(filename, states[current]);
      if (!contentHit) contentCache.set(content, states[current]);
      const pathValue = pathCache.get(filename), contentValue = contentCache.get(content);
      $('[data-input]').textContent = `${filename}  →  ${content}`;
      $('[data-path-value]').textContent = pathValue;
      $('[data-content-value]').textContent = contentValue;
      $('[data-path-state]').textContent = pathHit ? '命中：复用已有结果' : '未命中：计算并写入';
      $('[data-content-state]').textContent = contentHit ? '命中：复用相同内容' : '未命中：计算并写入';
      $('[data-path-result]').classList.toggle('wrong', pathValue !== states[current]);
      $('[data-path-result]').classList.toggle('right', pathValue === states[current]);
      $('[data-next]').disabled = current === states.length - 1;
      $('[data-rename]').disabled = filename !== 'screen.txt';
      const verdict = pathValue !== states[current] ? '按路径的缓存返回旧内容；按内容的缓存返回当前内容。' : '两种缓存现在都返回当前内容。';
      $('[data-demo-live]').textContent = `${action} 预期结果：${states[current]}。${verdict}`;
    };
    $('[data-next]').addEventListener('click', () => { if (current < states.length - 1) current++; update('更新了文件内容，文件名保持不变。'); });
    $('[data-rename]').addEventListener('click', () => { filename = 'screen-copy.txt'; update('只换文件名，内容不变。'); });
    $('[data-reset]').addEventListener('click', () => { current = 0; filename = 'screen.txt'; pathCache.clear(); contentCache.clear(); update('缓存已清空，重新载入第一份内容。'); });
    update('初始载入。');
  }
})();

(() => {
  'use strict';
  function packTernary(trits) {
    if (!Array.isArray(trits) || trits.length !== 5 || trits.some(value => !Number.isInteger(value) || value < -1 || value > 1)) {
      throw new RangeError('Choose exactly five values from -1, 0, and 1.');
    }
    return trits.reduce((packed, value, index) => packed + (value + 1) * (3 ** index), 0);
  }
  function unpackTernary(packed) {
    if (!Number.isInteger(packed) || packed < 0 || packed > 242) {
      throw new RangeError('A valid five-trit encoding is an integer from 0 to 242.');
    }
    return Array.from({ length: 5 }, (_, index) => Math.floor(packed / (3 ** index)) % 3 - 1);
  }
  function ternaryPython(trits) {
    packTernary(trits);
    return `trits = [${trits.join(', ')}]
packed = sum((value + 1) * 3 ** i for i, value in enumerate(trits))
restored = [(packed // 3 ** i) % 3 - 1 for i in range(5)]

assert 0 <= packed < 256
assert restored == trits
print("packed byte:", packed)
print("binary:", format(packed, "08b"))
print("restored:", restored)`;
  }
  // Node tests exercise the functions used by the page, without a second implementation.
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { packTernary, unpackTernary, ternaryPython };
  }
  if (typeof document === 'undefined') return;

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
  const ternaryDemo = document.querySelector('[data-ternary-demo]');
  if (ternaryDemo) {
    const $ = selector => ternaryDemo.querySelector(selector);
    const inputs = [...ternaryDemo.querySelectorAll('[data-trit]')];
    const initialValues = inputs.map(input => input.value);
    const feedback = $('[data-ternary-feedback]');
    const update = () => {
      const trits = inputs.map(input => Number(input.value));
      const packed = packTernary(trits);
      const restored = unpackTernary(packed);
      const matches = restored.every((value, index) => value === trits[index]);
      $('[data-ternary-packed]').textContent = String(packed);
      $('[data-ternary-binary]').textContent = packed.toString(2).padStart(8, '0');
      $('[data-ternary-restored]').textContent = `[${restored.join(', ')}]`;
      $('[data-ternary-equation]').textContent = trits.map((value, index) => `${value + 1} × ${3 ** index}`).join(' + ') + ` = ${packed}`;
      $('[data-ternary-verdict]').textContent = matches
        ? `往返一致：打包为 ${packed}，解包结果 [${restored.join(', ')}] 与输入完全相同。`
        : '往返不一致：解包结果与输入不同。';
      $('[data-ternary-code]').textContent = ternaryPython(trits);
      const body = `文章：${feedback.dataset.article}\n当前输入：[${trits.join(', ')}]\n打包整数：${packed}\n\n我卡在这里：\n`;
      feedback.href = `mailto:${feedback.dataset.email}?subject=${encodeURIComponent('Bonsai 三值编码小实验反馈')}&body=${encodeURIComponent(body)}`;
    };
    inputs.forEach(input => input.addEventListener('change', update));
    $('[data-ternary-reset]').addEventListener('click', () => {
      inputs.forEach((input, index) => { input.value = initialValues[index]; });
      update();
    });
    update();
    $('[data-ternary-inputs]').disabled = false;
    $('[data-ternary-reset]').disabled = false;
    $('.copy-code').disabled = false;
  }
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

(() => {
  'use strict';

  function matchesPr(row, { query = '', project = '', writtenOnly = false } = {}) {
    const words = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const search = (row.search || '').toLowerCase();
    return (!project || row.project === project)
      && (!writtenOnly || row.written === 'true')
      && words.every(word => search.includes(word));
  }

  function initPrIndex(root) {
    const keys = ['query', 'project', 'written', 'reset', 'status', 'empty'];
    const el = Object.fromEntries(keys.map(key => [key, root.querySelector(`[data-pr-${key}]`)]));
    if (Object.values(el).some(value => !value)) return false;
    const rows = Array.from(root.querySelectorAll('[data-pr-row]'));
    const render = () => {
      const filters = { query: el.query.value, project: el.project.value, writtenOnly: el.written.checked };
      let visible = 0;
      for (const row of rows) {
        row.hidden = !matchesPr(row.dataset, filters);
        if (!row.hidden) visible++;
      }
      el.status.textContent = `显示 ${visible} / ${rows.length} 条 PR`;
      el.empty.hidden = visible !== 0;
    };

    render();
    el.query.addEventListener('input', render);
    el.project.addEventListener('change', render);
    el.written.addEventListener('change', render);
    el.reset.addEventListener('click', event => {
      event.preventDefault();
      el.query.value = '';
      el.project.value = '';
      el.written.checked = false;
      render();
    });
    // The complete static list stays readable if initialization cannot finish.
    [el.query, el.project, el.written, el.reset].forEach(control => { control.disabled = false; });
    return true;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { matchesPr, initPrIndex };
  }
  if (typeof document === 'undefined') return;
  const start = () => document.querySelectorAll('[data-pr-index]').forEach(initPrIndex);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();

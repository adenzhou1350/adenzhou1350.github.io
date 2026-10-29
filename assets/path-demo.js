(() => {
  'use strict';
  const CWD = 'C:/lesson';
  const SOURCE = 'https://example.invalid/payload';
  const PRESETS = Object.freeze({
    bare: 'result.bin',
    nested: 'nested/result.bin',
    absolute: 'C:/lesson/result.bin',
  });

  // This is a six-case teaching model, not a general Windows path parser.
  function pathDemo(preset = 'bare', shape = 'list') {
    if (!Object.hasOwn(PRESETS, preset) || !['scalar', 'list'].includes(shape)) {
      throw new RangeError('Choose one of the three presets and scalar or list.');
    }
    const target = PRESETS[preset];
    const listed = shape === 'list';
    const normalized = listed || preset === 'absolute' ? target : `${CWD}/${target}`;
    const separator = normalized.lastIndexOf('/');
    const parent = separator < 0 ? '' : normalized.slice(0, separator);
    const sourceInput = listed ? [SOURCE] : SOURCE;
    const targetInput = listed ? [target] : target;
    const original = { action: 'mkdir', path: parent, canContinue: parent !== '' };
    const fixed = { action: parent ? 'mkdir' : 'skip', path: parent, canContinue: true };
    const api = [
      '# 假设 fs 是已配置好的 HTTPFileSystem；此处只展示参数形式。',
      '# example.invalid 是示例地址，不用于实际下载。',
      `source = ${JSON.stringify(SOURCE)}`,
      `fs.get(${listed ? '[source]' : 'source'}, ${JSON.stringify(targetInput)})`,
    ].join('\n');
    return { preset, shape, cwd: CWD, sourceInput, targetInput, normalized, parent, original, fixed, api };
  }

  function describeStep(step) {
    if (step.action === 'skip') return '父目录为空 → 跳过 os.makedirs，流程可继续（未执行下载）。';
    const call = `os.makedirs(${JSON.stringify(step.path)}, exist_ok=True)`;
    return `${call} → ${step.canContinue ? '流程可继续（未执行下载）。' : '空路径失败，流程停止。'}`;
  }

  function initPathDemo(root) {
    const keys = ['kind', 'shape', 'reset', 'input', 'target', 'parent', 'route', 'original', 'fixed', 'api', 'status'];
    const el = Object.fromEntries(keys.map(key => [key, root.querySelector(`[data-path-${key}]`)]));
    if (Object.values(el).some(value => !value)) return false;
    const render = (reset = false) => {
      const state = pathDemo(el.kind.value, el.shape.value);
      el.input.textContent = JSON.stringify(state.targetInput);
      el.target.textContent = state.normalized;
      el.parent.textContent = state.parent ? JSON.stringify(state.parent) : '""（空字符串）';
      el.route.textContent = state.shape === 'list'
        ? '源和目标同时传列表：走快捷分支，保留目标路径原样。'
        : '源和目标同时传标量：在本例中，目标会先转为绝对路径。';
      el.original.textContent = describeStep(state.original);
      el.fixed.textContent = describeStep(state.fixed);
      el.api.textContent = state.api;
      el.status.textContent = `${reset ? '已重置。' : ''}教学模拟：${state.original.canContinue
        ? '此组合两版均可继续流程。'
        : '列表裸名触发原版空目录错误；修复版跳过目录创建，流程可继续。'}未执行文件或网络操作。`;
    };
    render();
    el.kind.addEventListener('change', () => render());
    el.shape.addEventListener('change', () => render());
    el.reset.addEventListener('click', () => {
      el.kind.value = 'bare';
      el.shape.value = 'list';
      render(true);
    });
    // Keep the static default readable and the controls disabled if setup fails.
    [el.kind, el.shape, el.reset].forEach(control => { control.disabled = false; });
    return true;
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { pathDemo, describeStep, initPathDemo };
  }
  if (typeof document === 'undefined') return;
  const start = () => document.querySelectorAll('[data-path-demo]').forEach(initPathDemo);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();

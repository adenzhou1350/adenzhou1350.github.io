'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { matchesPr, initPrIndex } = require('../assets/pr-stories.js');

const records = [
  { project: 'fsspec/filesystem_spec', search: 'fsspec #2376 Fix async get 相对路径 result.bin', written: 'true' },
  { project: 'fsspec/filesystem_spec', search: 'fsspec #2302 Reject mixed backends', written: 'false' },
  { project: 'deepspeedai/DeepSpeed', search: 'DeepSpeed #8642 Fix scalar uint8 broadcasts []', written: 'true' },
  { project: 'lancedb/lancedb', search: 'LanceDB #4538 Handle empty batch iterables', written: 'true' },
  { project: 'tile-ai/tilelang', search: 'TileLang #3484 Fix TMA descriptor names', written: 'false' },
];

assert.equal(matchesPr(records[2], { query: '  SCALAR\t8642\nfix ' }), true);
assert.equal(matchesPr(records[0], { query: '相对路径 2376' }), true);
assert.equal(matchesPr(records[2], { query: 'scalar unknown' }), false, 'Every search word must match.');
assert.equal(matchesPr(records[2], { query: '[]' }), true, 'Search punctuation is literal, not a regular expression.');
assert.equal(matchesPr(records[0], { query: '.*' }), false);
assert.equal(matchesPr(records[2], { project: 'deepspeedai/DeepSpeed' }), true);
assert.equal(matchesPr(records[2], { project: 'deepspeedai/deepspeed' }), false, 'Repository selection is an exact match.');
assert.equal(matchesPr(records[1], { writtenOnly: true }), false, 'The string "false" must not count as a written story.');
assert.equal(matchesPr(records[0], { writtenOnly: true }), true);
assert.equal(matchesPr(records[0], { query: '2376', project: 'lancedb/lancedb', writtenOnly: true }), false);
assert.ok(records.every(record => matchesPr(record, { query: ' \t\n ' })));

function element(initial = {}) {
  const listeners = new Map();
  return {
    value: '', checked: false, disabled: true, hidden: false, textContent: '', ...initial,
    addEventListener(type, handler) {
      const callbacks = listeners.get(type) || [];
      callbacks.push(handler);
      listeners.set(type, callbacks);
    },
    emit(type) {
      const event = { defaultPrevented: false, preventDefault() { this.defaultPrevented = true; } };
      for (const handler of listeners.get(type) || []) handler(event);
      return event;
    },
  };
}

function fixture(data = records) {
  const controls = Object.fromEntries(['query', 'project', 'written', 'reset', 'status', 'empty'].map(key => [key, element()]));
  controls.empty.hidden = true;
  const rows = data.map(record => ({ dataset: { ...record }, hidden: false }));
  const root = {
    querySelector(selector) {
      const key = /^\[data-pr-(\w+)\]$/.exec(selector)?.[1];
      return controls[key] || null;
    },
    querySelectorAll(selector) {
      assert.equal(selector, '[data-pr-row]');
      return rows;
    },
  };
  const shown = () => rows.flatMap((row, index) => row.hidden ? [] : [index]);
  return { root, controls, rows, shown };
}

// Exercise the real browser initializer and its event handlers, not a second filter.
const demo = fixture();
assert.deepEqual(demo.shown(), [0, 1, 2, 3, 4], 'All server-rendered rows remain readable before JavaScript.');
assert.ok(['query', 'project', 'written', 'reset'].every(key => demo.controls[key].disabled));
assert.equal(initPrIndex(demo.root), true);
assert.ok(['query', 'project', 'written', 'reset'].every(key => !demo.controls[key].disabled));
assert.equal(demo.controls.status.textContent, '显示 5 / 5 条 PR');
assert.equal(demo.controls.empty.hidden, true);

demo.controls.query.value = 'fix';
demo.controls.query.emit('input');
assert.deepEqual(demo.shown(), [0, 2, 4]);
assert.equal(demo.controls.status.textContent, '显示 3 / 5 条 PR');

demo.controls.project.value = 'fsspec/filesystem_spec';
demo.controls.project.emit('change');
demo.controls.written.checked = true;
demo.controls.written.emit('change');
assert.deepEqual(demo.shown(), [0]);
assert.equal(demo.controls.status.textContent, '显示 1 / 5 条 PR');

demo.controls.query.value = 'backend';
demo.controls.query.emit('input');
assert.deepEqual(demo.shown(), [], 'An unwritten matching PR must stay hidden when written-only is selected.');
assert.equal(demo.controls.status.textContent, '显示 0 / 5 条 PR');
assert.equal(demo.controls.empty.hidden, false);
demo.controls.written.checked = false;
demo.controls.written.emit('change');
assert.deepEqual(demo.shown(), [1]);
assert.equal(demo.controls.empty.hidden, true);

demo.controls.project.value = 'deepspeedai/DeepSpeed';
demo.controls.project.emit('change');
assert.deepEqual(demo.shown(), []);
demo.controls.query.value = 'SCALAR\n8642';
demo.controls.query.emit('input');
assert.deepEqual(demo.shown(), [2]);
demo.controls.written.checked = true;
demo.controls.written.emit('change');
const resetEvent = demo.controls.reset.emit('click');
assert.equal(resetEvent.defaultPrevented, true);
assert.equal(demo.controls.query.value, '');
assert.equal(demo.controls.project.value, '');
assert.equal(demo.controls.written.checked, false);
assert.deepEqual(demo.shown(), [0, 1, 2, 3, 4]);
assert.equal(demo.controls.status.textContent, '显示 5 / 5 条 PR');
assert.equal(demo.controls.empty.hidden, true);

const incomplete = fixture();
delete incomplete.controls.status;
assert.equal(initPrIndex(incomplete.root), false);
assert.deepEqual(incomplete.shown(), [0, 1, 2, 3, 4]);
assert.ok(['query', 'project', 'written', 'reset'].every(key => incomplete.controls[key].disabled));

const emptyIndex = fixture([]);
assert.equal(initPrIndex(emptyIndex.root), true);
assert.equal(emptyIndex.controls.status.textContent, '显示 0 / 0 条 PR');
assert.equal(emptyIndex.controls.empty.hidden, false);

// Verify both browser script-loading paths using the actual shipped source.
const source = fs.readFileSync(path.join(__dirname, '../assets/pr-stories.js'), 'utf8');
for (const readyState of ['loading', 'complete']) {
  const first = fixture();
  const second = fixture([records[2]]);
  let onReady;
  const document = {
    readyState,
    querySelectorAll(selector) {
      assert.equal(selector, '[data-pr-index]');
      return [first.root, second.root];
    },
    addEventListener(name, handler, options) {
      assert.equal(name, 'DOMContentLoaded');
      assert.equal(options.once, true);
      onReady = handler;
    },
  };
  vm.runInNewContext(source, { document });
  if (readyState === 'loading') {
    assert.equal(first.controls.query.disabled, true);
    assert.equal(typeof onReady, 'function');
    onReady();
  }
  assert.equal(first.controls.query.disabled, false);
  assert.equal(second.controls.status.textContent, '显示 1 / 1 条 PR');
  first.controls.query.value = 'unmatched';
  first.controls.query.emit('input');
  assert.equal(first.controls.empty.hidden, false);
  assert.equal(second.controls.status.textContent, '显示 1 / 1 条 PR', 'Filtering one root must not affect another.');
  assert.deepEqual(second.shown(), [0]);
}

console.log('PASS: literal AND search, exact projects, written-only, combined filters, empty results, reset, safe initialization, and both browser startup paths.');

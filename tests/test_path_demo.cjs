'use strict';
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { pathDemo, describeStep, initPathDemo } = require('../assets/path-demo.js');

const cases = [];
for (const preset of ['bare', 'nested', 'absolute']) {
  for (const shape of ['scalar', 'list']) cases.push(pathDemo(preset, shape));
}
assert.equal(cases.length, 6);
assert.deepEqual(pathDemo(), cases.find(row => row.preset === 'bare' && row.shape === 'list'));
assert.equal(cases.filter(row => !row.original.canContinue).length, 1);
for (const row of cases) {
  const emptyParent = row.preset === 'bare' && row.shape === 'list';
  assert.equal(row.original.action, 'mkdir');
  assert.equal(row.original.path, row.parent);
  assert.equal(row.original.canContinue, !emptyParent);
  assert.equal(row.fixed.canContinue, true);
  assert.equal(row.fixed.action, emptyParent ? 'skip' : 'mkdir');
  assert.equal(row.fixed.path, row.parent);
  assert.ok(describeStep(row.fixed).includes('流程可继续（未执行下载）'));
  assert.ok(!describeStep(row.fixed).includes('os.makedirs(".",'));
  assert.equal(Array.isArray(row.sourceInput), row.shape === 'list');
  assert.equal(Array.isArray(row.targetInput), row.shape === 'list');
}
for (const args of [['other', 'scalar'], ['bare', 'array'], ['__proto__', 'list'], ['toString', 'list']]) {
  assert.throws(() => pathDemo(...args), RangeError);
}

// ntpath is the native Python Windows-path implementation, on any host OS.
// Run the displayed snippets with a recording fs, never a filesystem backend.
const python = spawnSync('python', ['-B', '-X', 'utf8', '-c', `
import json, ntpath, sys
rows = json.load(sys.stdin)
presets = {'bare': 'result.bin', 'nested': 'nested/result.bin', 'absolute': 'C:/lesson/result.bin'}
for row in rows:
    raw = presets[row['preset']]
    target = raw if row['shape'] == 'list' or ntpath.isabs(raw) else ntpath.join('C:/lesson', raw).replace('\\\\', '/')
    assert row['normalized'] == target
    assert row['parent'] == ntpath.dirname(target)
    calls = []
    class RecordingFS:
        def get(self, source, destination):
            calls.append((source, destination))
    exec(row['api'], {'fs': RecordingFS()})
    assert calls == [(row['sourceInput'], row['targetInput'])]
    assert (isinstance(calls[0][0], list) and isinstance(calls[0][1], list)) == (row['shape'] == 'list')
print('PASS: six targets and parents match Python ntpath; all displayed API snippets preserve source and target shapes.')
`], { input: JSON.stringify(cases), encoding: 'utf8' });
if (python.error) throw python.error;
assert.equal(python.status, 0, python.stderr);
process.stdout.write(python.stdout);

// Minimal DOM-shaped objects check the actual init/change/reset wiring without a browser.
const keys = ['kind', 'shape', 'reset', 'input', 'target', 'parent', 'route', 'original', 'fixed', 'api', 'status'];
const elements = Object.fromEntries(keys.map(key => [key, {
  value: key === 'kind' ? 'bare' : key === 'shape' ? 'list' : '',
  textContent: '', disabled: true, events: {},
  addEventListener(event, handler) { this.events[event] = handler; },
}]));
const root = { querySelector(selector) { return elements[selector.slice(11, -1)]; } };
assert.equal(initPathDemo(root), true);
assert.equal(elements.kind.disabled, false);
assert.equal(elements.shape.disabled, false);
assert.equal(elements.reset.disabled, false);
assert.equal(elements.parent.textContent, '""（空字符串）');
elements.kind.value = 'nested';
elements.kind.events.change();
assert.equal(elements.target.textContent, 'nested/result.bin');
assert.equal(elements.parent.textContent, '"nested"');
elements.shape.value = 'scalar';
elements.shape.events.change();
assert.equal(elements.target.textContent, 'C:/lesson/nested/result.bin');
assert.equal(elements.api.textContent, pathDemo('nested', 'scalar').api);
elements.reset.events.click();
assert.equal(elements.kind.value, 'bare');
assert.equal(elements.shape.value, 'list');
assert.equal(elements.api.textContent, pathDemo().api);
assert.ok(elements.status.textContent.startsWith('已重置。教学模拟：'));
assert.equal(initPathDemo({ querySelector() { return null; } }), false);
console.log('PASS: directory handling, closed presets, default state, initialization, change, reset, and incomplete markup.');

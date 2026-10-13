'use strict';
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { packTernary, unpackTernary, ternaryPython } = require('../assets/site.js');

// Cartesian inputs are independent of the encoder/decoder's base-3 implementation.
let inputs = [[]];
for (let position = 0; position < 5; position++) {
  inputs = inputs.flatMap(prefix => [-1, 0, 1].map(value => [...prefix, value]));
}
const encodings = new Set();
for (const trits of inputs) {
  const packed = packTernary(trits);
  assert.ok(Number.isInteger(packed) && packed >= 0 && packed < 256);
  assert.deepEqual(unpackTernary(packed), trits);
  encodings.add(packed);
}
assert.equal(inputs.length, 243);
assert.equal(encodings.size, 243, 'Every five-trit input must have its own byte value.');
assert.equal(Math.min(...encodings), 0);
assert.equal(Math.max(...encodings), 242);
for (const [trits, expected, binary] of [
  [[-1, 0, 1, -1, 1], 183, '10110111'],
  [[-1, -1, -1, -1, -1], 0, '00000000'],
  [[1, 1, 1, 1, 1], 242, '11110010'],
]) {
  assert.equal(packTernary(trits), expected);
  assert.equal(packTernary(trits).toString(2).padStart(8, '0'), binary);
}
for (const trits of [[], [-1, 0, 1], [-1, 0, 1, 2, 1], [-1, 0, 0.5, 1, 1], ['-1', 0, 1, -1, 1]]) {
  assert.throws(() => packTernary(trits), RangeError);
}
for (const packed of [-1, 243, 255, 1.5, '183', NaN]) {
  assert.throws(() => unpackTernary(packed), RangeError);
}

// Execute the actual copyable examples in Python, so snippet drift is caught too.
const samples = inputs.map(trits => ({ trits, packed: packTernary(trits), code: ternaryPython(trits) }));
const python = spawnSync('python', ['-c', `
import contextlib, io, json, sys
samples = json.load(sys.stdin)
for sample in samples:
    scope = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(sample['code'], scope)
    assert scope['trits'] == sample['trits']
    assert scope['packed'] == sample['packed']
    assert scope['restored'] == sample['trits']
print('PASS: all 243 copyable Python examples agree with the browser functions.')
`], { input: JSON.stringify(samples), encoding: 'utf8' });
if (python.error) throw python.error;
assert.equal(python.status, 0, python.stderr);
process.stdout.write(python.stdout);
console.log('PASS: 243 unique byte encodings, exhaustive round trips, known values, and invalid-input rejection.');

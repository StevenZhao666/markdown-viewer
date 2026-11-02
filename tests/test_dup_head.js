// v4.8.11 回归：同名标题 id 去重（真实抠 viewer.html 里的 _uniqHeadingIds 源码，用假 DOM 跑）
// 用法: node tests/test_dup_head.js
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'viewer.html'), 'utf8').replace(/\r\n/g, '\n');

function grab(name) {
  const i = src.indexOf('function ' + name + '(');
  if (i < 0) throw new Error('not found: ' + name);
  let d = 0, j = i;
  for (; j < src.length; j++) {
    if (src[j] === '{') d++;
    else if (src[j] === '}') { d--; if (d === 0) { j++; break; } }
  }
  return src.slice(i, j);
}
const _uniqHeadingIds = new Function(grab('_uniqHeadingIds') + '\nreturn _uniqHeadingIds;')();

let pass = 0, fail = 0;
function eq(actual, expected, label) {
  const a = JSON.stringify(actual), e = JSON.stringify(expected);
  if (a === e) { pass++; console.log('  PASS ' + label); }
  else { fail++; console.log('  FAIL ' + label + '\n    实际 ' + a + '\n    期望 ' + e); }
}
function run(ids) {
  const nodes = ids.map(id => ({ id }));
  _uniqHeadingIds({ querySelectorAll: () => nodes });
  return nodes.map(n => n.id);
}

// 1. 基本重名：第 2 处起 -2 / -3
eq(run(['h-定义', 'h-定义', 'h-定理', 'h-定义', 'h-定义']),
   ['h-定义', 'h-定义-2', 'h-定理', 'h-定义-3', 'h-定义-4'], '基本重名补后缀');

// 2. 天然 slug 撞上补出来的 id（"A" 与 "A 2" 都归一成 h-a-2 的情形）：必须仍唯一
eq(run(['h-a', 'h-a-2', 'h-a', 'h-a']),
   ['h-a', 'h-a-2', 'h-a-3', 'h-a-4'], '后缀与天然 id 撞车时继续顺延');

// 3. 空 id 不参与，也不影响其他标题
eq(run(['h-x', '', 'h-x']), ['h-x', '', 'h-x-2'], '空 id 跳过');

// 4. 不重名时原样不动（避免改变已有分享链接/锚点）
eq(run(['h-a', 'h-b', 'h-c']), ['h-a', 'h-b', 'h-c'], '无重名时不改动');

console.log('\n结果: ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);

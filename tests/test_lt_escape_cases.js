// 用 tests/t_cases.md 跑 renderMD -> 生成静态页 -> 交给 headless Chrome 解析
const fs = require('fs');

function makeRender(file) {
  const src = fs.readFileSync(file, 'utf8');
  function grab(name) {
    const i = src.indexOf('function ' + name + '(');
    if (i < 0) throw new Error('not found ' + name);
    let depth = 0, started = false;
    for (let k = i; k < src.length; k++) {
      const c = src[k];
      if (c === '{') { depth++; started = true; }
      else if (c === '}') { depth--; if (started && depth === 0) return src.slice(i, k + 1); }
    }
    throw new Error('unbalanced ' + name);
  }
  return new Function(grab('slug') + '\n' + grab('renderMD') + '\nreturn renderMD;')();
}

const R = makeRender('D:/MarkdownViewer/viewer.html');
const md = fs.readFileSync('D:/MarkdownViewer/tests/t_cases.md', 'utf8');
const blocks = md.split(/\n[ \t]*\n/);
let html = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>\n';
blocks.forEach((b, i) => {
  if (!b.trim()) return;
  html += '<div class="blk" data-i="' + i + '">' + R(b) + '</div>\n';
});
html += '</body></html>';
fs.writeFileSync('D:/MarkdownViewer/tests/t_cases.html', html, 'utf8');
console.log('块数:', blocks.filter(b => b.trim()).length, ' 输出:', html.length, '字节');

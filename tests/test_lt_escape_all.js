const fs = require('fs'), path = require('path');

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

const dir = 'D:/UM/MATH2003 数学分析 I Mathematical Analysis I/笔记';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
const jobs = [
  ['new', makeRender('D:/MarkdownViewer/viewer.html'), 'D:/MarkdownViewer/tests/t_all_new.html'],
  ['old', makeRender('D:/MarkdownViewer/backups/viewer-v4.7.0-before-lt-escape.html'), 'D:/MarkdownViewer/tests/t_all_old.html']
];
for (const [tag, render, outPath] of jobs) {
  let html = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>\n';
  let n = 0;
  for (const f of files) {
    const src = fs.readFileSync(path.join(dir, f), 'utf8');
    src.split(/\n[ \t]*\n/).forEach((b, i) => {
      if (!b.trim()) return;
      n++;
      html += '<div class="blk" data-f="' + f + '" data-i="' + i + '">' + render(b) + '</div>\n';
    });
  }
  html += '</body></html>';
  fs.writeFileSync(outPath, html, 'utf8');
  console.log(tag + ': ' + files.length + ' 个文件 / ' + n + ' 块 -> ' + outPath + '  (' + html.length + ' 字节)');
}

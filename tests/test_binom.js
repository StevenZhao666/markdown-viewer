// 从 viewer.html 提取 feParse / feTreeToLatex 并单元测试 binom
const fs=require('fs');
const html=fs.readFileSync('D:/MarkdownViewer/viewer.html','utf8');

function extractFn(src, name, nextName){
  const start=src.indexOf('function '+name+'(');
  if(start<0) throw name+' not found';
  const end=src.indexOf('function '+nextName+'(');
  if(end<0) throw nextName+' not found';
  return src.slice(start,end);
}

const code = extractFn(html,'feParse','feTreeToLatex') + '\n' +
             extractFn(html,'feTreeToLatex','feNodeHTML');
// feTreeToLatex 里 case mtx 引用 feMtxLatex——提供 stub（测试不触发 mtx）
const stub='function feMtxLatex(){return "";}';
(0,eval)(code+'\n'+stub+';globalThis.__feParse=feParse;globalThis.__feTreeToLatex=feTreeToLatex;');

const feParse=globalThis.__feParse, feTreeToLatex=globalThis.__feTreeToLatex;
let pass=0,fail=0;
function t(name,cond,extra){
  if(cond){pass++;console.log('  PASS',name);}
  else{fail++;console.log('  FAIL',name,extra||'');}
}

// 1. feParse binom
let tree=feParse('\\binom{7}{2}');
t('feParse \\binom{7}{2} 生成 binom 节点', tree.length===1&&tree[0].type==='binom', JSON.stringify(tree,tree));
t('top=7', tree[0]&&tree[0].top&&tree[0].top[0]&&tree[0].top[0].value==='7');
t('bottom=2', tree[0]&&tree[0].bottom&&tree[0].bottom[0]&&tree[0].bottom[0].value==='2');

// 2. feTreeToLatex binom
t('feTreeToLatex 输出 \\binom{7}{2}', feTreeToLatex(tree)==='\\binom{7}{2}', feTreeToLatex(tree));

// 3. 嵌套: binom 里 frac
tree=feParse('\\binom{\\frac{1}{2}}{4}');
t('嵌套 binom{frac} 解析', tree.length===1&&tree[0].type==='binom'&&tree[0].top[0].type==='frac');
t('嵌套输出', feTreeToLatex(tree)==='\\binom{\\frac{1}{2}}{4}', feTreeToLatex(tree));

// 4. 回归: frac 仍然正常
tree=feParse('\\frac{a}{b}');
t('回归 frac', feTreeToLatex(tree)==='\\frac{a}{b}', feTreeToLatex(tree));

// 5. 回归: sum
tree=feParse('\\sum_{i=1}^{n} i');
t('回归 sum', tree.length===1&&tree[0].type==='sum'&&feTreeToLatex(tree).includes('\\sum'), feTreeToLatex(tree));

// 6. 回归: text 节点
tree=feParse('x^2');
t('回归 subsup', tree.length===1&&tree[0].type==='subsup'&&feTreeToLatex(tree)==='x^{2}', feTreeToLatex(tree));

console.log('\n结果:', pass+' passed, '+fail+' failed');
process.exit(fail?1:0);

const fs = require('fs');

function makeRender(file) {
  const src = fs.readFileSync(file, 'utf8');
  function grab(name) {
    const i = src.indexOf('function ' + name + '(');
    if (i < 0) throw new Error('not found ' + name + ' in ' + file);
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

const OLD = makeRender('D:/MarkdownViewer/backups/viewer-v4.7.0-before-lt-escape.html');
const NEW = makeRender('D:/MarkdownViewer/viewer.html');

const cases = {
  A_定义行: '**2.1.6 Definition** $a-b\\in\\mathbb{P}$ 时写 $a>b$（或 $b<a$）；$a-b\\in\\mathbb{P}\\cup\\{0\\}$ 时写 $a\\ge b$。',
  B_邻域行: '由 2.2.2(c) 的严格版：$x\\in V_\\varepsilon(a)\\iff a-\\varepsilon<x<a+\\varepsilon$，即**以 $a$ 为中心、长 $2\\varepsilon$ 的开区间**。',
  C_简单不等式: '若 $x<y$ 则成立。',
  D_details: '<details><summary>答案</summary>',
  E_代码块: '```\nif (a<b) { return a; }\n```',
  F_display公式: '$$0<x<1$$',
  G_正文裸小于: '正文里的裸 < 也要处理：a < b。',
  H_表格: '| 情形 | 结果 |\n|---|---|\n| $x<y$ | $y>x$ |\n',
  I_列表: '- $0<x<1$ 时成立',
  J_引用: '> 若 $k<n$ 则 $I_n\\subseteq I_k$。',
  K_行内代码: '写 `a<b` 这样。',
  L_和号: '集合 A & B 的并，price &amp; tax。',
  M_大于号: '若 $x>y$ 则 $y<x$。',
  N_粗斜体: '***重点***：$u_1<u_2$。',
  O_链接: '[见这里](http://x.com?a=1&b=2) 与 $a<b$。',
  P_多重小于: '$2\\le2z_k<2z_{k+1}<4\\Rightarrow \\sqrt2\\le z_{k+1}<z_{k+2}<2$',
  Q_星号上标: '例如 $x^*=-\\varepsilon/2$ 满足 $\\lvert x^*-0\\rvert<\\varepsilon$ 却在 $I$ 外。',
  R_标题公式: '### 3.3 $\\sup$ 的四个等价说法（印刷 p.38）',
  S_公式含方括号: '取 $[x,y]\\subseteq S$ 与 $a_{[1]}$。',
  T_公式与粗体相邻: '**重点** $x^*$ **收尾**',
  U_转义美元: '价格 \\$5 与公式 $a+b$。',
  V_公式含反引号与下划线: '记号 $x_{n_k}$ 与 $a*b$。',
  W_表格含绝对值: '| | 说法 |\n|---|---|\n| (b) | $\\forall\\varepsilon>0\\ \\exists K:\\ |x_n-x|<\\varepsilon$ |\n',
  X_表格多列公式: '| 情形 | 不等式 | 结果 |\n|---|---|---|\n| (i) | $|x-1|<|x|$ | $x>1/2$ |\n'
};

let same = 0, diff = 0;
for (const k of Object.keys(cases)) {
  const o = OLD(cases[k]), n = NEW(cases[k]);
  if (o === n) { same++; console.log('[相同] ' + k); }
  else {
    diff++;
    console.log('[不同] ' + k);
    console.log('   old: ' + o);
    console.log('   new: ' + n);
  }
}
console.log('\n共 ' + (same + diff) + ' 例：相同 ' + same + '，不同 ' + diff);

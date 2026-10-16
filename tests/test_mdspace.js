// 从 viewer.html 提取真实 renderMD（slug 用 stub，避免带入 DOM 代码）
const fs=require('fs');
const html=fs.readFileSync('D:/MarkdownViewer/viewer.html','utf8');
const m=html.match(/function renderMD\([\s\S]*?\r?\n\}\r?\n/);
if(!m) throw 'renderMD not found';
const code='function slug(t){return t.trim().toLowerCase().replace(/\\s+/g,"-").replace(/[^\\w\\u4e00-\\u9fa5-]/g,"");}\n'+m[0];
(0,eval)(code+';globalThis.__renderMD=renderMD;');
const renderMD=globalThis.__renderMD;

let pass=0,fail=0;
function t(name,cond,extra){
  if(cond){pass++;console.log('  PASS',name);}
  else{fail++;console.log('  FAIL',name,'\n    '+extra);}
}

// 1. 1 个空行 → 1 个 md-space
let out=renderMD('AAA\n\nBBB');
t('单空行→md-space', out.includes('<div class="md-space"></div>'), out);

// 2. 3 个空行 → 3 个 md-space
out=renderMD('AAA\n\n\n\nBBB');
const cnt=(out.match(/<div class="md-space"><\/div>/g)||[]).length;
t('3空行→3个md-space', cnt===3, out+' (count='+cnt+')');

// 3. 公式块内换行不受影响（占位符保护）
out=renderMD('$$\na\nb\n$$');
t('$$多行公式内部不转md-space', !out.includes('<div class="md-space">'), out);

// 4. 代码块内空行不受影响
out=renderMD('```\na\n\nb\n```');
t('代码块内部空行不转md-space', !out.includes('<div class="md-space">'), out);

// 5. 列表之间空行
out=renderMD('- a\n\n- b');
t('列表间空行→md-space', out.includes('<div class="md-space">'), out);

// 6. 空行前后是公式占位符（用户作业场景：题+多个空行+公式）
out=renderMD('Find the number\n\n$$\\binom{7}{2}$$\n\nAnswer');
t('作业场景(空行+公式)', out.includes('<div class="md-space">')&&out.includes('math-block'), out);

console.log('\n结果:', pass+' passed, '+fail+' failed');
process.exit(fail?1:0);

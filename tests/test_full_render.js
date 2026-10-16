const fs=require('fs');
function slug(t){return t.trim().toLowerCase().replace(/\s+/g,'-').replace(/[^\w\u4e00-\u9fa5-]/g,'');}
function renderMD(text){ /* 同前 */ 
  let h=text;
  const _codeBlocks=[];
  h=h.replace(/```(\w*)\n([\s\S]*?)```/g,(_,lang,code)=>{
    _codeBlocks.push(code.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'));
    return `\x00CB${_codeBlocks.length-1}\x00`;
  });
  h=h.replace(/((?:^\|.+\|\n)+)/gm,function(block){
    const lines=block.trim().split('\n');
    if(lines.length<2) return block;
    const parseRow=r=>r.split('|').slice(1,-1).map(c=>c.trim());
    const headerCells=parseRow(lines[0]);
    const dataLines=lines.slice(1).filter(l=>!/^\|[-:| ]+\|$/.test(l));
    let html='<table>';
    html+='<thead><tr>'+headerCells.map(c=>'<th>'+c+'</th>').join('')+'</tr></thead>';
    if(dataLines.length){
      html+='<tbody>';
      dataLines.forEach(l=>{
        const cells=parseRow(l);
        while(cells.length<headerCells.length) cells.push('');
        html+='<tr>'+cells.slice(0,headerCells.length).map(c=>'<td>'+c+'</td>').join('')+'</tr>';
      });
      html+='</tbody>';
    }
    html+='</table>';
    return html;
  });
  const _mathBlocks=[];
  h=h.replace(/\$\$([\s\S]*?)\$\$/g,(m)=>{_mathBlocks.push(m);return `\x00MB${_mathBlocks.length-1}\x00`;});
  h=h.replace(/`([^`]+)`/g,'<code>$1</code>');
  h=h.replace(/^#### (.+)$/gm,(_,t)=>`<h4 id="${slug(t)}">${t}</h4>`);
  h=h.replace(/^### (.+)$/gm,(_,t)=>`<h3 id="${slug(t)}">${t}</h3>`);
  h=h.replace(/^## (.+)$/gm,(_,t)=>`<h2 id="${slug(t)}">${t}</h2>`);
  h=h.replace(/^# (.+)$/gm,(_,t)=>`<h1 id="${slug(t)}">${t}</h1>`);
  h=h.replace(/\*\*\*(.+?)\*\*\*/g,'<strong><em>$1</em></strong>');
  h=h.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
  h=h.replace(/\*(.+?)\*/g,'<em>$1</em>');
  h=h.replace(/!\[([^\]]*)\]\(([^)]+)\)/g,'<img src="$2" alt="$1">');
  h=h.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank">$1</a>');
  h=h.replace(/^---$/gm,'<hr>');
  h=h.replace(/^> (.+)$/gm,'<blockquote>$1</blockquote>');
  h=h.replace(/^- (.+)$/gm,'<li>$1</li>');
  h=h.replace(/(<li>.*<\/li>\n?)+/g,'<ul>$&</ul>');
  h=h.replace(/^(?!<[a-z]|$)(.+)$/gm,'<p>$1</p>');
  h=h.replace(/<p>\s*<\/p>/g,'');
  h=h.replace(/\x00MB(\d+)\x00/g,(_,i)=>`<div class="math-block">${_mathBlocks[i]}</div>`);
  h=h.replace(/<p>\x00CB(\d+)\x00<\/p>/g,(_,i)=>`<pre><code>${_codeBlocks[i]}</code></pre>`);
  h=h.replace(/\x00CB(\d+)\x00/g,(_,i)=>`<pre><code>${_codeBlocks[i]}</code></pre>`);
  return h;
}
function _parseBlocks(text){
  const lines=text.split('\n');
  const blocks=[]; let cur=[];
  function flush(){
    if(cur.length && cur.some(l=>l.trim())){blocks.push(cur.join('\n'));}
    cur=[];
  }
  for(let i=0;i<lines.length;i++){
    const l=lines[i];
    if(/^#{1,4}\s/.test(l)){flush(); cur.push(l); flush();}
    else if(/^---$/.test(l)&&!(lines[i-1]||'').startsWith('|')){flush(); cur.push(l); flush();}
    else cur.push(l);
  }
  flush();
  const out=blocks.map(b=>b.replace(/\n{3,}/g,'\n\n')).filter(b=>b.trim());
  if(out.length===0) out.push('');
  return out;
}

const file='/d/UM/MATH2005 概率论 Probability/assignment/MATH_2005_UM_Assignment_1_marker.md';
// 从bash路径读取不行，用进程参数
const src=process.argv[2];
const text=fs.readFileSync(src,'utf8');
const blocks=_parseBlocks(text);
console.log('总块数:', blocks.length);
blocks.forEach((raw,idx)=>{
  console.log(`--- 块 ${idx} (${raw.split('\n').length}行) raw: ${JSON.stringify(raw.slice(0,80))}`);
  console.log(renderMD(raw));
  console.log();
});

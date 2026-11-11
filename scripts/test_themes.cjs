// Exercise actual template initializers and cycle functions without panel/network access.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
for(const panel of ['sub','marzban','pasarguard']){
 const raw=fs.readFileSync(path.join(__dirname,'..',panel+'.html'),'utf8');
 for(const initial of [0,1,2,3]){
  const classes=new Set(),elements=new Map();
  const element=id=>{if(!elements.has(id))elements.set(id,{attributes:{},innerHTML:'',setAttribute(k,v){this.attributes[k]=v;}});return elements.get(id);};
  const document={body:{classList:{add:c=>classes.add(c),remove:(...cs)=>cs.forEach(c=>classes.delete(c))}},getElementById:element,querySelector:()=>element('theme-meta')};
  const context=vm.createContext({document,playClickSound(){}});
  const themeSource=raw.slice(raw.indexOf('let themeIndex = '),raw.indexOf('function toggleCyberTheme')).replace(/let themeIndex = \d;/,`let themeIndex = ${initial};`);
  vm.runInContext(themeSource,context);
  const initStart=raw.indexOf('// Apply ',raw.indexOf("document.addEventListener('DOMContentLoaded',()=>{"));
  const init=raw.slice(initStart,raw.indexOf('  function hideLoader()',initStart));
  vm.runInContext(init,context);
  const names=['red','green','blue','purple'];
  const verify=expected=>{
   assert.deepEqual([...classes],expected==='red'?[]:['theme-'+expected],panel+' theme classes');
   assert.equal(element('theme-meta').attributes.content,element('logo-icon').attributes.stroke);
   assert.match(element('theme-cycle-btn').innerHTML,/<svg/);
   if(expected==='purple'){
    assert.equal(element('g-stop1').attributes['stop-color'],'#b78bff');
    assert.equal(element('g-stop2').attributes['stop-color'],'#e1caff');
    assert.equal(element('theme-meta').attributes.content,'#b78bff');
   }
  };
  verify(names[initial]);
  for(let i=1;i<=8;i++){vm.runInContext('cycleTheme()',context);verify(names[(initial+i)%4]);}
 }
 // Fully rendered fixtures must contain syntactically valid inline JavaScript.
 for(const theme of ['red','green','blue','purple']){
  const file=panel==='marzban'&&theme==='red'?'index.html':panel+'-'+theme+'.html';
  const fixture=fs.readFileSync(path.join(__dirname,'..','preview',file),'utf8');
  for(const match of fixture.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new vm.Script(match[1]);
 }
}
console.log('PASS: all 4 initial themes, two complete theme cycles, purple gradients and browser chrome in all 3 panels; fixture JavaScript parses');

/* Ghost Sub status: SVG assets, fixed feed only, no browser-side port scans. */
const GhostNodes = (() => {
  const aliases={DE:['germany','german','آلمان'],PL:['poland','لهستان'],NL:['netherlands','holland','هلند'],FR:['france','فرانسه'],GB:['united kingdom','uk','britain','انگلیس'],US:['united states','usa','america','آمریکا'],TR:['turkey','türkiye','ترکیه'],FI:['finland','فنلاند'],SE:['sweden','سوئد'],CA:['canada','کانادا'],AE:['united arab emirates','uae','امارات'],IR:['iran','ایران'],RU:['russia','روسیه']};
  const cleanName=n=>n.replace(/[\u{1F1E6}-\u{1F1FF}]{2}/gu,'').trim();
  function country(name){
    const flag=name.match(/[\u{1F1E6}-\u{1F1FF}]{2}/u);
    if(flag)return [...flag[0]].map(c=>String.fromCharCode(c.codePointAt(0)-0x1f1e6+65)).join('');
    const words=name.toLowerCase().replace(/[_|·\-]/g,' ');
    for(const [code,names] of Object.entries(aliases)){
      if(new RegExp('(^|[^a-z])'+code+'([^a-z]|$)').test(name))return code;
      if(names.some(n=>new RegExp('(^|[^a-zآ-ی])'+n+'([^a-zآ-ی]|$)','i').test(words)))return code;
    }
    return '';
  }
  function flag(code){
    const bands=(a,b,c)=>`<path fill="${a}" d="M0 0h32v7H0z"/><path fill="${b}" d="M0 7h32v7H0z"/><path fill="${c}" d="M0 14h32v7H0z"/>`;
    const vertical=(a,b,c)=>`<path fill="${a}" d="M0 0h11v21H0z"/><path fill="${b}" d="M11 0h10v21H11z"/><path fill="${c}" d="M21 0h11v21H21z"/>`;
    const cross=(bg,fg)=>`<path fill="${bg}" d="M0 0h32v21H0z"/><path fill="${fg}" d="M9 0h5v21H9zM0 8h32v5H0z"/>`;
    const designs={DE:bands('#25252a','#d12d41','#efc554'),NL:bands('#c93646','#f7f4ef','#254c9b'),RU:bands('#f7f4ef','#3153a1','#c43646'),PL:'<path fill="#f7f4ef" d="M0 0h32v11H0z"/><path fill="#d23952" d="M0 11h32v10H0z"/>',FR:vertical('#2456a6','#f7f4ef','#db3d4e'),IR:bands('#249f70','#f7f4ef','#d13e47')+'<path d="M14 9v4m4-4v4m-5-1h6" stroke="#d13e47" stroke-width="1.5"/>',FI:cross('#f7f4ef','#2c5aa4'),SE:cross('#3067ad','#edc647'),AE:bands('#27956c','#faf7f1','#22252d')+'<path fill="#d13e47" d="M0 0h8v21H0z"/>',TR:'<path fill="#ce3045" d="M0 0h32v21H0z"/><circle cx="14" cy="10.5" r="6" fill="#fff"/><circle cx="16" cy="9.5" r="4.8" fill="#ce3045"/><path fill="#fff" d="m22 7 1 2.3 2.5.3-1.8 1.7.5 2.5-2.2-1.2-2.2 1.2.5-2.5-1.8-1.7 2.5-.3z"/>',GB:'<path fill="#25478b" d="M0 0h32v21H0z"/><path stroke="#fff" stroke-width="5" d="m0 0 32 21M32 0 0 21"/><path stroke="#d0394b" stroke-width="2" d="m0 0 32 21M32 0 0 21"/><path stroke="#fff" stroke-width="8" d="M16 0v21M0 10.5h32"/><path stroke="#d0394b" stroke-width="4" d="M16 0v21M0 10.5h32"/>',US:bands('#c73c51','#fff','#c73c51')+'<path fill="#fff" d="M0 3h32v2H0zM0 9h32v2H0zM0 15h32v2H0z"/><path fill="#2e4b8f" d="M0 0h14v12H0z"/><path fill="#fff" d="m5 3 1 2 2 .2-1.5 1.4.5 2-2-1-2 1 .5-2L2 5.2 4 5z"/>',CA:vertical('#cf3c4a','#fff','#cf3c4a')+'<path fill="#cf3c4a" d="m16 4 1.5 4 2-1-.7 3 3 1-4 3 .3 2h-1.5v3h-1v-3h-1.5l.3-2-4-3 3-1-.7-3 2 1z"/>'};
    if(!designs[code])return '<svg viewBox="0 0 32 22" fill="none" aria-hidden="true"><circle cx="16" cy="11" r="9" stroke="currentColor"/><ellipse cx="16" cy="11" rx="4" ry="9" stroke="currentColor"/><path d="M7 11h18M9 6h14M9 16h14" stroke="currentColor"/></svg>';
    return '<svg viewBox="0 0 32 21" aria-hidden="true">'+designs[code]+'</svg>';
  }
  function endpoint(link){
    try {
      let protocol=link.split(':')[0].toLowerCase(),host,port;
      if(protocol==='vmess'){
        let raw=link.slice(8).split('#')[0].replace(/-/g,'+').replace(/_/g,'/');
        const o=JSON.parse(atob(raw.padEnd(Math.ceil(raw.length/4)*4,'=')));host=o.add;port=Number(o.port);
      }else if(['vless','trojan','ss'].includes(protocol)){
        let value=link;
        if(protocol==='ss'&&!link.slice(5).split('#')[0].includes('@')){
          let raw=link.slice(5).split('#')[0].replace(/-/g,'+').replace(/_/g,'/');
          value='ss://'+atob(raw.padEnd(Math.ceil(raw.length/4)*4,'='))+'#';
        }
        const u=new URL(value);host=u.hostname.replace(/^\[|\]$/g,'');port=Number(u.port);
      }else return null;
      if(typeof host!=='string'||!host||!Number.isInteger(port)||port<1||port>65535)return null;
      return {host:host.toLowerCase().replace(/\.$/,''),port};
    }catch(_){return null;}
  }
  // Endpoint identifiers are public lookup keys, not authentication or secrets.
  // Local fallback also supports preview pages where WebCrypto is unavailable.
  function digest(text){
    const bytes=new TextEncoder().encode(text),length=Math.ceil((bytes.length+9)/64)*64;
    const data=new Uint8Array(length);data.set(bytes);data[bytes.length]=128;
    const view=new DataView(data.buffer);view.setUint32(length-4,bytes.length*8);
    const h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    const k=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    const rot=(x,n)=>(x>>>n)|(x<<(32-n)),w=new Uint32Array(64);
    for(let offset=0;offset<length;offset+=64){
      for(let i=0;i<16;i++)w[i]=view.getUint32(offset+i*4);
      for(let i=16;i<64;i++){const a=w[i-15],b=w[i-2];w[i]=(w[i-16]+(rot(a,7)^rot(a,18)^(a>>>3))+w[i-7]+(rot(b,17)^rot(b,19)^(b>>>10)))>>>0;}
      let [a,b,c,d,e,f,g,j]=h;
      for(let i=0;i<64;i++){
        const t=(j+(rot(e,6)^rot(e,11)^rot(e,25))+((e&f)^(~e&g))+k[i]+w[i])>>>0;
        const u=((rot(a,2)^rot(a,13)^rot(a,22))+((a&b)^(a&c)^(b&c)))>>>0;
        j=g;g=f;f=e;e=(d+t)>>>0;d=c;c=b;b=a;a=(t+u)>>>0;
      }
      [a,b,c,d,e,f,g,j].forEach((v,i)=>h[i]=(h[i]+v)>>>0);
    }
    return h.map(v=>v.toString(16).padStart(8,'0')).join('').slice(0,24);
  }

  async function key(link){
    const e=endpoint(link);if(!e)return null;
    if(!globalThis.crypto?.subtle)return digest(e.host+':'+e.port);
    const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(e.host+':'+e.port));
    return [...new Uint8Array(b)].map(v=>v.toString(16).padStart(2,'0')).join('').slice(0,24);
  }
  function fresh(node,feed,now=Date.now()/1000){
    if(!node||feed?.schema!==1||feed.measurement!=='tcp_connect_samples')return false;
    const interval=feed.interval_seconds;
    if(typeof interval!=='number'||interval<30||interval>3600)return false;
    const age=now-node.last_checked,feedAge=now-feed.generated_at;
    return Number.isFinite(age)&&node.last_checked>0&&age>=-30&&age<=Math.max(180,interval*3)&&feedAge>=-30&&feedAge<=Math.max(180,interval*3);
  }
  function spark(history){
    const values=Array.isArray(history)?history.slice(0,24):[];
    let path='',connected=false;const dots=[];
    for(let i=0;i<24;i++){
      const v=values[i];
      if(typeof v!=='number'||!Number.isFinite(v)||v<0||v>100){connected=false;continue;}
      const x=(4+i*292/23).toFixed(2),y=(49-v*.42).toFixed(2);
      path+=(connected?' L ':' M ')+x+' '+y;connected=true;
      dots.push('<circle cx="'+x+'" cy="'+y+'" r="2.1"/>');
    }
    return '<svg class="node-spark" viewBox="0 0 300 56" preserveAspectRatio="none" role="img" aria-label="Reachability sample history"><path class="node-spark-grid" d="M4 7H296M4 49H296"/>'+(path?'<path class="node-spark-line" d="'+path+'"/>'+dots.join(''):'')+'</svg>';
  }
  return {country,flag,cleanName,endpoint,key,fresh,spark};
})();
if(typeof module!=='undefined')module.exports=GhostNodes;
let ghostFeed=null;
function nodeText(){return lang==='fa'?{up:'قابل دسترس',down:'پاسخ نداده',unstable:'ناپایدار',unknown:'نامشخص',details:'دسترسی از نقطهٔ پایش',sample:'نمونه‌های موفق',coverage:'مدت مشاهده',last:'آخرین بررسی',source:'نقطهٔ پایش',note:'بررسی پورت TCP؛ سلامت کامل کانفیگ و آپ‌تایم سیستم‌عامل را تأیید نمی‌کند.',none:'دادهٔ تازه نداریم',hours:'ساعت',ago:'ثانیه پیش',history:'تاریخچهٔ ۲۴ ساعت؛ بخش خالی یعنی داده نداریم'}:{up:'Reachable',down:'No response',unstable:'Unstable',unknown:'Unknown',details:'Monitor reachability',sample:'Successful samples',coverage:'Observed span',last:'Last checked',source:'Probe location',note:'TCP port check; not full configuration health or OS uptime.',none:'No recent data',hours:'hours',ago:'seconds ago',history:'24-hour history; empty segments mean no samples'};}
function nodeIcon(state){
 const paths={up:'m5 12 4 4L19 6',down:'m6 6 12 12M18 6 6 18',unstable:'M3 12h4l3-7 4 14 3-7h4',unknown:'M12 8v4m0 4h.01'};
 return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="'+paths[state]+'"/></svg>';
}
function updateGhostOverview(){
 const element=document.getElementById('v-srv-status');if(!element)return;
 const rows=[...document.querySelectorAll('.has-node-status')];
 const current=rows.map(r=>ghostFeed?.nodes?.[r.dataset.nodeKey]).filter(n=>GhostNodes.fresh(n,ghostFeed));
 const up=current.filter(n=>n.state==='up').length;
 element.textContent=current.length?up+'/'+rows.length+' '+(lang==='fa'?'قابل دسترس':'reachable'):nodeText().unknown;
 element.style.color=!current.length?'var(--text2)':up===rows.length?'#7de6b0':'#f3c57e';
 element.title=nodeText().note;
 const dot=element.parentElement.querySelector('.server-dot');if(dot){dot.className='server-dot';dot.style.background=element.style.color;}
}
function updateNodeRow(row){
 updateGhostOverview();
 const t=nodeText(),key=row.dataset.nodeKey,node=ghostFeed?.nodes?.[key];
 const known=GhostNodes.fresh(node,ghostFeed),state=known&&['up','down','unstable'].includes(node.state)?node.state:'unknown';
 const button=row.querySelector('.node-status');if(!button)return;
 button.className='node-status node-'+state;button.innerHTML=nodeIcon(state)+'<span></span>';
 button.querySelector('span').textContent=t[state];button.title=t.note;
 const code=known&&/^[A-Z]{2}$/.test(node.country||'')?node.country:row.dataset.country;
 const flag=row.querySelector('.node-flag');flag.innerHTML=GhostNodes.flag(code);flag.title=code||t.unknown;
 const details=row.querySelector('.node-details');details.replaceChildren();
 const heading=document.createElement('div');heading.className='node-chart-heading';
 const label=document.createElement('span');label.textContent=lang==='fa'?'دسترسی · ۲۴ ساعت':'Reachability · 24h';heading.appendChild(label);
 const value=document.createElement('strong');value.textContent='—';heading.appendChild(value);details.appendChild(heading);
 const graph=document.createElement('div');graph.className='node-spark-wrap';details.appendChild(graph);
 if(known){
  if(Number.isInteger(node.samples)&&Number.isInteger(node.successful_samples)&&node.samples>0&&node.successful_samples>=0&&node.successful_samples<=node.samples)value.textContent=(100*node.successful_samples/node.samples).toFixed(1)+'%';
  graph.innerHTML=GhostNodes.spark(node.history);
  graph.title=t.note+' '+t.source+': '+String(ghostFeed.probe_label||'—').slice(0,80)+' · '+t.last+': '+Math.max(0,Math.round(Date.now()/1000-node.last_checked))+' '+t.ago;
 }else{
  const empty=document.createElement('span');empty.className='node-spark-empty';empty.textContent=t.none;graph.appendChild(empty);
 }
 const axis=document.createElement('div');axis.className='node-chart-axis';
 const first=document.createElement('span');first.textContent=lang==='fa'?'۲۴ ساعت قبل':'24h ago';
 const last=document.createElement('span');last.textContent=lang==='fa'?'اکنون':'Now';axis.append(first,last);details.appendChild(axis);
 if(known&&Number.isFinite(node.observed_seconds)&&node.observed_seconds>=0){const span=document.createElement('span');span.className='node-chart-coverage';span.textContent=(node.observed_seconds/3600).toFixed(1)+' '+t.hours+' · '+(lang==='fa'?'دادهٔ ثبت‌شده':'recorded span');details.appendChild(span);}

}
function attachNodeStatus(row,link,name){
 row.classList.add('has-node-status');row.dataset.country=GhostNodes.country(name);
 const flag=document.createElement('span');flag.className='node-flag';flag.innerHTML=GhostNodes.flag(row.dataset.country);row.prepend(flag);
 row.querySelector('.cfg-name').textContent=GhostNodes.cleanName(name);
 const info=document.createElement('div');info.className='cfg-info';info.append(row.querySelector('.cfg-name'),row.querySelector('.proto-tag'));row.insertBefore(info,row.querySelector('.cfg-qr'));
 const button=document.createElement('button');button.type='button';button.className='node-status node-unknown';button.setAttribute('aria-expanded','true');
 const details=document.createElement('div');details.className='node-details';details.hidden=false;
 button.addEventListener('click',()=>{details.hidden=!details.hidden;button.setAttribute('aria-expanded',String(!details.hidden));updateNodeRow(row);});
 row.appendChild(button);row.appendChild(details);updateNodeRow(row);
 GhostNodes.key(link).then(k=>{if(k){row.dataset.nodeKey=k;updateNodeRow(row);}}).catch(()=>{});
}
async function refreshGhostStatus(){
 const url=document.querySelector('meta[name=ghost-status-feed]')?.content;
 if(url){
  const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),6000);
  try{
   const target=new URL(url,location.href);
   if(target.protocol!=='https:'&&target.origin!==location.origin)throw Error('Feed requires HTTPS');
   const response=await fetch(target.href,{credentials:'omit',cache:'no-store',signal:controller.signal});
   if(!response.ok)throw Error('Unavailable status');
   const text=await response.text();if(text.length>100000)throw Error('Oversized status');
   const value=JSON.parse(text);if(value.schema!==1||!value.nodes||typeof value.nodes!=='object')throw Error('Invalid status');
   ghostFeed=value;
  }catch(_){ghostFeed=null;}finally{clearTimeout(timer);}
 }
 document.querySelectorAll('.has-node-status').forEach(updateNodeRow);
}
document.addEventListener('DOMContentLoaded',()=>{refreshGhostStatus();setInterval(()=>{if(!document.hidden)refreshGhostStatus();},60000);});

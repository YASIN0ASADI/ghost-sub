const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/../sub.html','utf8');const block=html.slice(html.indexOf('let ghostUsageCache=null;'),html.indexOf('function renderChart()'));
async function run(scheme,port,base=''){
 const calls=[],nodes={};const location=new URL(scheme+'//144.31.14.215:2096/base/abcdefghijklmnop');
 const context={URL,Date,AbortController,setTimeout,clearTimeout,encodeURIComponent,location,RAW:{subUrl:location.href},lang:'en',T:{en:{}},renderChart:()=>{},document:{getElementById:id=>nodes[id]??(nodes[id]={style:{}}),querySelector:s=>({content:s.includes('ghost-usage-port')?port:base}),querySelectorAll:()=>[]},fetch:async(url,opts)=>{calls.push([url,opts.credentials,opts.referrerPolicy]);return{ok:true,text:async()=>JSON.stringify({schema:1,source:'sampled_3xui_counters',updated_at:Date.now()/1000,points:[{t:Date.now(),used:500}]})}}};
 vm.createContext(context);vm.runInContext('let _chartPoints=null;let _chartRange="week";'+block,context);await vm.runInContext('loadUsageChart()',context);return calls;
}
(async()=>{
 assert.deepEqual(await run('http:',18090),[['http://144.31.14.215:18090/ghost-usage/abcdefghijklmnop','omit','no-referrer']]);
 assert.deepEqual(await run('https:',18090),[['https://144.31.14.215:18090/ghost-usage/abcdefghijklmnop','omit','no-referrer']]);
 assert.deepEqual(await run('http:',0,'https://other.example/history/'),[]);
 console.log('PASS: usage chart retains original URL, sends only own token to same-host data port, and blocks foreign-origin/insecure HTTPS fallback');
})().catch(e=>{console.error(e);process.exit(1)});

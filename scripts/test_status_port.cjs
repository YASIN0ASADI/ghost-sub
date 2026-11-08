const fs=require('fs'),vm=require('vm'),assert=require('assert');
async function check(scheme,port,feed=''){
 const fetched=[];const location=new URL(scheme+'//144.31.14.215:2096/sub/dummy');
 const context={URL,TextEncoder,AbortController,setTimeout,clearTimeout,location,module:{exports:{}},document:{querySelector:s=>({content:s.includes('ghost-status-port')?port:feed}),querySelectorAll:()=>[],addEventListener:()=>{}},fetch:async(url,opts)=>{fetched.push([url,opts.credentials]);return {ok:true,text:async()=>'{"schema":1,"nodes":{}}'}}};
 vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/status_ui.js','utf8'),context);await vm.runInContext('refreshGhostStatus()',context);return fetched;
}
(async()=>{
 assert.deepEqual(await check('http:',18090),[['http://144.31.14.215:18090/ghost-status.json','omit']]);
 assert.deepEqual(await check('https:',18090),[]);
 assert.deepEqual(await check('http:',0),[]);
 assert.deepEqual(await check('http:',0,'http://other.example/status'),[]);
 console.log('PASS: original subscription stays unchanged; background feed uses same-host port; HTTPS blocks insecure fallback');
})().catch(e=>{console.error(e);process.exit(1)});

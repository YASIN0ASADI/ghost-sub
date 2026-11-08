const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
// Evaluate only the pure core; UI hooks require a real browser and are exercised separately.
const source=fs.readFileSync(__dirname+'/status_ui.js','utf8').split('let ghostFeed=null;')[0];
const sandbox={module:{exports:{}},URL,atob,TextEncoder,crypto:crypto.webcrypto};vm.createContext(sandbox);vm.runInContext(source,sandbox);
const n=sandbox.module.exports;
assert.equal(n.country('🇩🇪 Germany - 1'),'DE');assert.equal(n.country('Germany'),'DE');assert.equal(n.country('آلمان - ۱'),'DE');assert.equal(n.country('PL - 2'),'PL');assert.equal(n.country('speedy'),'');assert.equal(n.cleanName('🇩🇪 Germany'),'Germany');
assert(n.flag('DE').includes('<svg'));assert(!n.flag('XX').includes('undefined'));
const endpoint=n.endpoint('vless://id@Node.Example:443?security=tls#DE');assert.equal(endpoint.host,'node.example');assert.equal(endpoint.port,443);
assert.equal(n.endpoint('not a valid link'),null);assert.equal(n.endpoint('vless://id@node.example#DE'),null);
const vmess=Buffer.from(JSON.stringify({add:'node.example',port:'443'})).toString('base64');assert.equal(n.endpoint('vmess://'+vmess).host,'node.example');
const feed={schema:1,measurement:'tcp_connect_samples',interval_seconds:60,generated_at:1000};assert(n.fresh({last_checked:1000},feed,1001));assert(!n.fresh({last_checked:1},feed,1001));assert(!n.fresh({last_checked:1000},{...feed,generated_at:1},1001));
n.key('vless://id@Node.Example:443#DE').then(id=>{assert.equal(id,crypto.createHash('sha256').update('node.example:443').digest('hex').slice(0,24));console.log('PASS: country flags, parsing, freshness and monitor/browser endpoint identity');});

const fallback={module:{exports:{}},URL,atob,TextEncoder};vm.createContext(fallback);vm.runInContext(source,fallback);
Promise.all(['node.example','a'.repeat(120)+'.example','127.0.0.1','[2001:db8::1]'].map(async host=>{const link='vless://id@'+host+':443#DE';const actual=await fallback.module.exports.key(link);const normalized=host.replace(/^\[|\]$/g,'');assert.equal(actual,crypto.createHash('sha256').update(normalized+':443').digest('hex').slice(0,24));})).then(()=>console.log('PASS: fallback identifiers match SHA256 for DNS, IPv4, IPv6 and multiple blocks'));

const gaps=n.spark([100,null,0]);assert.equal((gaps.match(/ M /g)||[]).length,2);assert(!gaps.includes(' L '));assert(!n.spark([null,undefined,-1,101,NaN]).includes('node-spark-line'));assert(n.spark(Array(24).fill(100)).includes(' L '));console.log('PASS: line chart preserves unknown gaps and never plots absent data as uptime');

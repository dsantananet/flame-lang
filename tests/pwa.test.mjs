import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import vm from 'node:vm';
const root=new URL('../web/meteo/',import.meta.url);
function worker(){
 const handlers={},deleted=[],added=[];let skipped=0,claimed=0;
 const scope='https://example.test/flame-lang/web/meteo/';
 const context={URL,Set,self:{registration:{scope},clients:{claim:async()=>{claimed++;}},skipWaiting:()=>{skipped++;},addEventListener:(name,handler)=>handlers[name]=handler},caches:{open:async()=>({addAll:async list=>added.push(...list),match:async()=>null}),keys:async()=>['unrelated-cache','ignispyro-meteo-old','ignispyro-meteo-1.1.0'],delete:async key=>{deleted.push(key);}},fetch:()=>{}};
 vm.runInNewContext(readFileSync(new URL('sw.js',root),'utf8'),context);
 return {handlers,deleted,added,scope,skipped:()=>skipped,claimed:()=>claimed};
}
test('manifest references actual PNG icons at correct dimensions',()=>{
 const m=JSON.parse(readFileSync(new URL('manifest.webmanifest',root),'utf8'));
 assert.equal(m.display,'standalone');assert.equal(m.scope,'./');
 for(const icon of m.icons){const b=readFileSync(new URL(icon.src,root));const size=Number(icon.sizes.split('x')[0]);assert.equal(b.readUInt32BE(16),size);assert.equal(b.readUInt32BE(20),size);}
});
test('offline installation contains complete local resources and waits for update consent',async()=>{
 const w=worker();let pending;
 w.handlers.install({waitUntil:p=>pending=p});await pending;
 assert.ok(w.added.length>15);for(const url of w.added){const path=url.slice(w.scope.length)||'index.html';assert.ok(existsSync(new URL(path,root)),path);}
 assert.equal(w.skipped(),0);
 w.handlers.message({data:{type:'APPLY_UPDATE'}});assert.equal(w.skipped(),1);
});
test('worker never intercepts secrets, weather API, or unrelated files',()=>{
 const w=worker();
 for(const url of ['https://api.weather.com/v2/pws/observations/current?apiKey=test','https://api.ipma.pt/observations.json','https://example.test/api/wu','https://example.test/flame-lang/.wu-key.enc']){
  let intercepted=false;w.handlers.fetch({request:{method:'GET',url},respondWith:()=>intercepted=true});assert.equal(intercepted,false,url);
 }
});
test('activation cleans only its old caches and preserves unrelated application storage',async()=>{
 const w=worker();let pending;w.handlers.activate({waitUntil:p=>pending=p});await pending;
 assert.deepEqual(w.deleted,['ignispyro-meteo-old']);assert.equal(w.claimed(),1);
});

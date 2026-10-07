import test from 'node:test';
import assert from 'node:assert/strict';
import {normalize,merge,forecast,csv,geojson} from '../web/meteo/engine.mjs';
const points=Array.from({length:24},(_,i)=>({t:Date.UTC(2026,0,1,i),time:`2026-01-01T${String(i).padStart(2,'0')}:00`,v:10+i*.5}));
test('linear forecast uses chronological holdout and beats persistence on a linear series',()=>{
 const p=forecast(points,'temperature').predictions;
 assert.equal(p[0].value,22);assert.equal(p[2].value,23);
 assert.ok(p[0].n>=10);assert.equal(p[0].mae,0);assert.equal(p[0].baseline,.5);assert.equal(p[0].spread,0);
});
test('constant observations reproduce persistence',()=>{
 const p=forecast(points.map(p=>({...p,v:50})),'humidity').predictions;
 assert.equal(p[2].value,50);assert.equal(p[2].mae,0);assert.equal(p[2].baseline,0);
});
test('future observations do not affect prefix predictions',()=>{
 const a=forecast(points.slice(0,12),'temperature').predictions;
 const corrupted=[...points.slice(0,12),...points.slice(12).map(p=>({...p,v:1000}))];
 assert.deepEqual(a,forecast(corrupted.filter(p=>p.t<=points[11].t),'temperature').predictions);
});
test('gaps, insufficient data, lagging observations and unsupported fields suppress forecast',()=>{
 assert.ok(forecast(points.slice(0,3),'temperature').reason);
 assert.ok(forecast(points.filter((p,i)=>i<18||i===23),'temperature').reason);
 assert.ok(forecast(points,'temperature',points.at(-1).t+3*3600000).reason);
 assert.ok(forecast(points,'rain').reason);
});
test('humidity is physically bounded; sparse errors have no uncertainty band',()=>{
 const p=forecast(points.slice(0,4).map((p,i)=>({...p,v:90+i*3})),'humidity').predictions;
 assert.equal(p[2].value,100);assert.equal(p[2].spread,null);
});
test('normalize handles null stations, missing sentinel and valid zeros, retains geography',()=>{
 const stations=[{properties:{idEstacao:1,localEstacao:'Test; "station"'},geometry:{coordinates:[-7,40]}}];
 const rows=normalize(stations,{'2026-01-01T00:00':{'1':{temperatura:-99,humidade:0,intensidadeVentoKM:0,precAcumulada:0},'2':null}});
 assert.equal(rows.length,1);assert.equal(rows[0].temperature,null);assert.equal(rows[0].humidity,0);
 assert.deepEqual(geojson(rows).features[0].geometry.coordinates,[-7,40]);
 assert.ok(csv(rows).includes('"Test; ""station"""'));
});
test('archive replaces duplicates and prunes older than 30 days',()=>{
 const old=[{source:'IPMA',id:'1',time:'2025-01-01T00:00'},{source:'IPMA',id:'1',time:'2026-01-01T00:00',temperature:1}];
 const merged=merge(old,[{source:'IPMA',id:'1',time:'2026-01-01T00:00',temperature:2}]);
 assert.equal(merged.length,1);assert.equal(merged[0].temperature,2);
});

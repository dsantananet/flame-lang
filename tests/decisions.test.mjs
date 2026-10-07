import test from 'node:test';
import assert from 'node:assert/strict';
import {assess} from '../web/meteo/decisions.mjs';
const rows=Array.from({length:24},(_,i)=>({time:`2026-01-01T${String(i).padStart(2,'0')}:00`,temperature:20,humidity:40,wind:10,rain:1}));
test('complete hourly coverage yields rainfall sum and degree-days',()=>{const r=assess(rows,rows.at(-1).time);assert.equal(r.rain24,24);assert.equal(r.degreeDays,10);});
test('missing hours do not imply dry conditions or zero degree-days',()=>{const r=assess(rows.slice(1),rows.at(-1).time);assert.equal(r.rain24,null);assert.equal(r.degreeDays,null);});
test('null inputs never produce a reassuring fire classification',()=>{const r=assess([{...rows.at(-1),temperature:null}],rows.at(-1).time);assert.equal(r.fire,'Dados insuficientes');});
test('combination and heavy hourly rain activate distinct indicators',()=>{const r=assess([{...rows.at(-1),temperature:38,humidity:15,wind:55,rain:15}],rows.at(-1).time);assert.equal(r.civil.length,4);assert.ok(r.agro.length);});
test('stale observations suspend assessment and custom thresholds matter',()=>{assert.ok(assess(rows,'2026-01-02T03:00').unavailable);const r=assess(rows,rows.at(-1).time,{heat:19});assert.ok(r.agro.length);assert.ok(r.civil.length);});

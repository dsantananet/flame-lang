export const fields = {temperature: ['Temperatura', '°C', 'temperatura'], humidity: ['Humidade', '%', 'humidade'], wind: ['Vento', 'km/h', 'intensidadeVentoKM'], rain: ['Precipitação horária', 'mm', 'precAcumulada']};
export function number(value) { return typeof value === 'number' && Number.isFinite(value) && value !== -99 ? value : null; }
// IPMA timestamps do not include an offset: arithmetic uses source clock, without labelling it UTC.
export function clock(value) { return Date.parse(value.endsWith('Z') || /[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`); }
export function normalize(stations, data) {
  const lookup = new Map(stations.map(s => [String(s.properties.idEstacao), s]));
  const rows = [];
  for (const [time, values] of Object.entries(data)) {
    if (!Number.isFinite(clock(time))) continue;
    for (const [id, v] of Object.entries(values)) {
      if (!v) continue;
      const s = lookup.get(id); if (!s) continue;
      const [lon, lat] = s.geometry.coordinates;
      rows.push({id, name:s.properties.localEstacao, time, lon, lat, source:'IPMA', temperature:number(v.temperatura), humidity:number(v.humidade), wind:number(v.intensidadeVentoKM), rain:number(v.precAcumulada)});
    }
  }
  return rows;
}
export function merge(oldRows, newRows) {
  const entries = new Map([...oldRows, ...newRows].filter(r => Number.isFinite(clock(r.time))).map(r => [`${r.source}:${r.id}:${r.time}`,r]));
  const end = [...entries.values()].reduce((latest,r)=>Math.max(latest,clock(r.time)),-Infinity);
  return [...entries.values()].filter(r=>clock(r.time)>=end-30*86400000).sort((a,b)=>clock(a.time)-clock(b.time));
}
export function series(rows, id, field) {
  return rows.filter(r=>r.id===id && number(r[field])!==null).map(r=>({t:clock(r.time),v:r[field],time:r.time})).sort((a,b)=>a.t-b.t);
}
function estimate(points, horizon, field) {
  const last = points.at(-1); if (!last) return null;
  const fit = points.filter(p=>p.t>=last.t-5*3600000);
  if (fit.length<4 || last.t-fit[0].t<3*3600000 || fit.some((p,i)=>i && p.t-fit[i-1].t>2*3600000)) return null;
  const xs=fit.map(p=>(p.t-last.t)/3600000), mx=xs.reduce((a,b)=>a+b)/xs.length, my=fit.reduce((a,p)=>a+p.v,0)/fit.length;
  const den=xs.reduce((a,x)=>a+(x-mx)**2,0);
  const raw=fit.reduce((a,p,i)=>a+(xs[i]-mx)*(p.v-my),0)/den;
  const limit=field==='temperature'?2:10;
  const slope=Math.max(-limit,Math.min(limit,raw));
  const value=last.v+slope*horizon;
  return field==='humidity'?Math.max(0,Math.min(100,value)):value;
}
export function forecast(points, field, now=null) {
  if (!['temperature','humidity'].includes(field)) return {reason:'Previsão disponível apenas para temperatura e humidade.'};
  if (!points.length) return {reason:'Sem observações válidas.'};
  if (now!==null && now-points.at(-1).t>2*3600000) return {reason:'Última observação tem mais de 2 horas; previsão suspensa.'};
  const result=[];
  for (let h=1;h<=3;h++) {
    const value=estimate(points,h,field); if (value===null) return {reason:'Requer pelo menos 4 observações válidas em 6 horas, sem grandes lacunas.'};
    const errors=[],baseline=[];
    for (let i=3;i<points.length;i++) {
      const pred=estimate(points.slice(0,i+1),h,field); if (pred===null) continue;
      const actual=points.find((p,j)=>j>i && p.t===points[i].t+h*3600000); if (!actual) continue;
      errors.push(Math.abs(actual.v-pred)); baseline.push(Math.abs(actual.v-points[i].v));
    }
    const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
    const q=errors.length>=10?[...errors].sort((a,b)=>a-b)[Math.ceil(errors.length*.9)-1]:null;
    result.push({h,value,time:new Date(points.at(-1).t+h*3600000).toISOString().slice(0,16),n:errors.length,mae:mean(errors),baseline:mean(baseline),spread:q});
  }
  return {predictions:result};
}
export function csv(rows, delimiter=';') {
  const keys=['source','id','name','time','lon','lat','temperature','humidity','wind','rain'];
  const quote=v=>'"'+String(v??'').replaceAll('"','""')+'"';
  return '\uFEFF'+[keys,...rows.map(r=>keys.map(k=>r[k]))].map(r=>r.map(quote).join(delimiter)).join('\r\n');
}
export function geojson(rows) { return {type:'FeatureCollection',features:rows.filter(r=>Number.isFinite(r.lon)&&Number.isFinite(r.lat)).map(r=>({type:'Feature',geometry:{type:'Point',coordinates:[r.lon,r.lat]},properties:r}))}; }

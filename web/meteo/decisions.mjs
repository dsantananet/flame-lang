import {clock, number} from './engine.mjs';
export const defaults={frost:0,heat:35,dry:20,wind:30,gustRisk:50,rain:10,base:10};
export function assess(history,selectedTime,thresholds=defaults,predictions=[]){
 const t={...defaults,...thresholds},end=clock(selectedTime);
 const latest=history.filter(r=>clock(r.time)<=end).at(-1);
 if(!latest||end-clock(latest.time)>2*3600000)return {unavailable:true,reason:'Sem observação da estação nas últimas 2 horas do horário selecionado.'};
 const recent=history.filter(r=>clock(r.time)>end-24*3600000&&clock(r.time)<=end);
 const hourly=new Map();
 for(const r of recent)hourly.set(Math.floor(clock(r.time)/3600000),r);
 const valid=key=>[...hourly.values()].map(r=>r[key]).filter(v=>number(v)!==null);
 const temp=valid('temperature'),humidity=valid('humidity'),rain=valid('rain');
 const result={unavailable:false,coverage:hourly.size,temperatureCoverage:temp.length,rainCoverage:rain.length,min:temp.length?Math.min(...temp):null,max:temp.length?Math.max(...temp):null,rain24:rain.length===24?rain.reduce((a,b)=>a+b,0):null,degreeDays:temp.length===24?temp.reduce((a,b)=>a+Math.max(0,b-t.base),0)/24:null,agro:[],civil:[],fire:'Dados insuficientes'};
 if(result.min!==null&&result.min<=t.frost)result.agro.push('Frio observado no período: verificar danos nas culturas sensíveis. Temperatura do ar não confirma geada à superfície.');
 if(result.max!==null&&result.max>=t.heat)result.agro.push('Calor observado no período: verificar sinais de stress nas culturas.');
 if(number(latest.wind)!==null&&latest.wind>=t.wind)result.agro.push('Vento acima do limiar: avaliar exposição de culturas e trabalhos no terreno.');
 if(humidity.length&&Math.min(...humidity)<=t.dry)result.agro.push('Humidade do ar baixa: verificar stress hídrico; não equivale a humidade do solo.');
 if(predictions.some(p=>p.value<=t.frost))result.agro.push('A tendência experimental de temperatura cruza o limiar de frio nas próximas 3 horas.');
 if(predictions.some(p=>p.value>=t.heat))result.agro.push('A tendência experimental de temperatura cruza o limiar de calor nas próximas 3 horas.');
 const known=key=>number(latest[key])!==null;
 if(known('temperature')&&known('humidity')&&known('wind')){
  const combination=latest.temperature>=t.heat&&latest.humidity<=t.dry&&latest.wind>=t.wind;
  result.fire=combination?'Combinação de calor, secura e vento acima dos limiares':'Combinação de limiares não atingida';
  if(combination)result.civil.push('Condições meteorológicas potencialmente favoráveis à propagação de incêndio. Consultar perigo oficial, combustível e contexto local.');
 }
 if(known('wind')&&latest.wind>=t.gustRisk)result.civil.push('Vento médio acima do limiar: avaliar exposição de estruturas e operações. Sem dados de rajadas.');
 if(known('rain')&&latest.rain>=t.rain)result.civil.push('Chuva horária acima do limiar: acompanhar drenagem e áreas vulneráveis. Não estima inundação nem caudais.');
 if(known('temperature')&&latest.temperature>=t.heat)result.civil.push('Calor acima do limiar: acompanhar população vulnerável e exposição no exterior.');
 return result;
}

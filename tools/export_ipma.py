"""Exportação IPMA para CSV e GeoJSON; apenas biblioteca padrão."""
import argparse, csv, json, os, time, urllib.request
from pathlib import Path
from datetime import datetime, timezone
BASE='https://api.ipma.pt/open-data/observation/meteorology/stations/'
FIELDS={'temperatura':'temperatura_c','humidade':'humidade_pct','intensidadeVentoKM':'vento_kmh','precAcumulada':'precipitacao_hora_mm','pressao':'pressao_hpa','radiacao':'radiacao_kj_m2','idDireccVento':'vento_classe'}

def fetch(name, cache, refresh):
    p=cache/name
    if not refresh and p.exists() and time.time()-p.stat().st_mtime<600:
        return json.loads(p.read_text())
    with urllib.request.urlopen(BASE+name,timeout=30) as response:
        data=json.load(response)
    tmp=p.with_suffix('.tmp'); tmp.write_text(json.dumps(data)); tmp.replace(p)
    return data

def normalize(stations, observations, station=None):
    lookup={str(s['properties']['idEstacao']):s for s in stations}
    rows=[]
    for timestamp, values in sorted(observations.items()):
        datetime.fromisoformat(timestamp)
        for sid, obs in sorted(values.items()):
            if station and sid!=station: continue
            if obs is None: continue
            feature=lookup.get(sid,{})
            coords=feature.get('geometry',{}).get('coordinates',[None,None])
            row={'fonte':'IPMA','estacao_id':sid,'estacao_nome':feature.get('properties',{}).get('localEstacao',''), 'data_hora_fonte':timestamp,'fuso_fonte':'nao indicado no contrato consultado','longitude':coords[0],'latitude':coords[1]}
            missing=[]
            for key,label in FIELDS.items():
                value=obs.get(key)
                if value is None or value==-99: missing.append(label); value=None
                row[label]=value
            row['campos_ausentes']='|'.join(missing)
            rows.append(row)
    if not rows: raise ValueError('Sem observações para a seleção')
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path.cwd() / 'meteo-data')
    p.add_argument('--station',help='ID IPMA opcional; não é o ID Weather Underground')
    p.add_argument('--refresh',action='store_true')
    args=p.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    cache=args.output/'cache'; cache.mkdir(exist_ok=True)
    rows=normalize(fetch('stations.json',cache,args.refresh),fetch('observations.json',cache,args.refresh),args.station)
    for name,delimiter in [('observacoes.csv',','),('observacoes_excel.csv',';')]:
        target=args.output/name; tmp=target.with_suffix('.tmp')
        with tmp.open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=delimiter)
            writer.writeheader(); writer.writerows(rows)
        tmp.replace(target)
    features=[{'type':'Feature','geometry':{'type':'Point','coordinates':[r['longitude'],r['latitude']]},'properties':r} for r in rows if r['longitude'] is not None and r['latitude'] is not None]
    (args.output/'observacoes.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False),encoding='utf-8')
    (args.output/'manifesto.json').write_text(json.dumps({'fonte':BASE,'recolhido_utc':datetime.now(timezone.utc).isoformat(),'registos':len(rows),'estacoes':len({r['estacao_id'] for r in rows}),'primeiro_horario_fonte':min(r['data_hora_fonte'] for r in rows),'ultimo_horario_fonte':max(r['data_hora_fonte'] for r in rows),'nota':'Observações pontuais, não grelhas GRIB; não assumir timezone da fonte.'},ensure_ascii=False,indent=2))
    print(f'{len(rows)} observações exportadas para {args.output}')
if __name__=='__main__':
    try: main()
    except Exception as exc:
        raise SystemExit(f'Falha na exportação IPMA: {type(exc).__name__}: {exc}')

# IgnisPyro — gateway do servidor de simulação

Primeira implementação técnica da fronteira entre **Meteo** e **Simulação**.
O serviço valida uma mensagem meteorológica versionada, mas **não calcula propagação nem integra PyreCast ainda**.

## Iniciar no servidor (rede privada)

```sh
export IGNISPYRO_SIM_TOKEN='definir-no-gestor-de-segredos'
python3 -m simulation.server
```

Por omissão escuta apenas em `127.0.0.1:8102`. Colocar atrás de proxy HTTPS com autenticação, limites de pedidos e registos, caso seja necessário acesso remoto. Nunca guardar o token no Git.

- `GET /health`: estado do gateway.
- `POST /api/v1/weather/validate`: validar dados de entrada, com cabeçalho `Authorization: Bearer ...`. **Não inicia simulação**.

Exemplo de entrada:

```json
{
  "schema_version": "1.0",
  "source": "IPMA",
  "valid_time": "2026-10-11T06:00:00Z",
  "geometry_crs": "EPSG:4326",
  "point": {"lat": 39.8, "lon": -7.5},
  "variables": {
    "temperature_c": 25,
    "relative_humidity_pct": 35,
    "wind_speed_ms": 4,
    "wind_direction_deg": 270
  },
  "quality_flags": []
}
```

O adaptador do Meteo deverá converter unidades e tempos para este contrato, preservando proveniência. O motor real exigirá também combustíveis, DEM, ignição, horizontes e validação. PyreCast será avaliado como motor opcional, não assumido como instalado.

Testes: `python3 -m unittest discover -s tests -p 'test_simulation_contract.py'`.

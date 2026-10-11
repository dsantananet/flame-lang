# IgnisPyro — fronteiras dos módulos

## Meteo (`web/meteo/`)
**Objetivo:** observações e previsões meteorológicas, cartografia, análise da atmosfera e exportação.

- IPMA, Weather Underground (IALDEI10 e estações autorizadas), fontes NOAA GFS/GRIB2.
- Mapa com cidades, rios, florestas, relevo e linha temporal.
- Seleção de todas as estações, uma estação ou até três para comparação.
- Meteogramas A4 e dados exportáveis; tefigramas a partir de perfis verticais de modelos ou sondagens devidamente identificados.
- FWI e componentes, Haines e C-Haines, CAPE, CIN, HDW, VPD, PBLH.
- Pyrocast apenas como investigação de condições atmosféricas associadas a pyroCb; validar licença e disponibilidade antes de integrar.
- Logótipo original IgnisPyro no PWA, relatórios e interface.

**Excluído:** previsão de perímetros de incêndio, simulação de propagação, PyreCast, impactos do fogo.

## Simulação (`simulation/`, módulo futuro)
**Objetivo:** modelos de propagação e cenários, usando dados meteorológicos do Meteo como entradas com proveniência.

- Avaliar PyreCast: código, licença, pesos, dados de entrada, domínio de aplicação e validação para Portugal.
- Propagação anisotrópica, combustível, declive, perímetros, isócronas e incerteza.
- Comparar resultados com perímetros observados, nunca anunciar validação sem testes.

## Contrato de integração futuro
A passagem Meteo → Simulação deverá ser uma API versionada com:
`timestamp_utc`, `source`, `model_cycle`, `valid_time`, `geometry_crs`, `resolution`, `units`, `quality_flags` e `variables`.
A meteorologia não deverá importar o motor de propagação. Credenciais permanecem no servidor.

## Estado
Documento de arquitetura e separação de âmbito. Não constitui implementação nem validação dos módulos novos.

- Meteo: https://github.com/dsantananet/flame-lang/issues/2

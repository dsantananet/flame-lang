# Flame Meteo

Aplicação de observações meteorológicas inspirada no fluxo de mapas e séries temporais do zyGrib. Usa estações pontuais, não grelhas GRIB. O interpretador Flame original permanece separado: esta versão não executa regras Flame nem calcula índices de incêndio.

## Abrir e instalar

Sem pacotes Python adicionais; Python 3.10+ para o servidor opcional. Num checkout existente:

```sh
python3 meteo_server.py
```

Abra o caminho `/web/meteo/` no servidor na porta 8000. Para publicar como site estático, sirva o repositório com GitHub Pages; o ponto de entrada é `web/meteo/index.html`, também ligado na página inicial. As observações IPMA funcionam diretamente no navegador por CORS. O mapa usa Leaflet via unpkg e contornos Natural Earth (domínio público) incluídos no repositório; não depende de servidores de mosaicos. O fundo é uma referência geográfica simplificada, não cartografia de detalhe. Requer Internet. Não há ferramentas SIG de desktop ou zyGrib instaladas por esta aplicação.

## Observações

Obtém `stations.json` e `observations.json` da API oficial IPMA. Os dados -99 e nulos são tratados como ausentes; zero é válido. A precipitação IPMA é o acumulado horário em mm. O mapa não interpola estações nem apresenta as cores como uma superfície de previsão. Selecionar estação/variável e mover o cursor temporal permite consultar e animar observações. Os gráficos usam os últimos 24 horários da fonte.

O histórico fica no armazenamento local do navegador até 30 dias relativamente à observação mais recente. Não é um arquivo central: limpar o navegador elimina esse histórico. A aplicação consulta a janela disponível na API, que não garante a recuperação de intervalos perdidos. Exportar regularmente para preservar dados. Os horários IPMA não contêm offset na resposta; a aplicação preserva-os e não afirma que são UTC ou hora local. A aritmética de tendência usa as diferenças do relógio da fonte; confirmar fuso antes de cruzar IPMA com outra fonte. A IALDEI10 tem timestamps UTC explícitos.

## Previsão experimental

Extrapolação de tendência linear das últimas seis horas, ancorada na última observação, horizontes de 1, 2 e 3 horas. Requer quatro amostras válidas distribuídas por pelo menos três horas, sem lacunas superiores a duas horas. Taxa limitada a ±2 °C/h ou ±10 pontos percentuais/h; humidade limitada entre 0 e 100%. Estes limites são escolhas iniciais, não parâmetros calibrados para cada estação. A previsão é local à estação selecionada; não usa ainda estações vizinhas, modelos numéricos, radar ou satélite. Vento e chuva são apenas observados nesta versão.

A seleção de um horário passado calcula uma previsão a partir do passado desse horário, não uma previsão emitida agora. Dados da estação atrasados mais de duas horas face à hora selecionada impedem o cálculo. Confirme sempre o horário da fonte e o estado de atualização: a aplicação pode continuar a mostrar histórico após falhas de rede. Não é um sistema de avisos oficiais.

A avaliação cronológica reproduz o cálculo em instantes anteriores, usando somente dados já observados nesse instante, e compara a previsão com uma observação posterior no horizonte exato. Mostra MAE, MAE da persistência (último valor observado) e número de casos para cada horizonte. A faixa ± usa o percentil 90 do erro absoluto histórico se houver pelo menos dez casos; não é um intervalo probabilístico calibrado. O desempenho na janela disponível não comprova qualidade operacional ou melhoria noutras épocas. Estações novas podem não ter avaliação suficiente.

## Excel e SIG

- CSV de observações: UTF-8 com BOM, delimitador `;`, decimais com ponto. No Excel use **Dados → De Texto/CSV**, selecionando delimitador e configuração decimal adequados.
- Campos `temperature` (°C), `humidity` (%), `wind` (km/h) e `rain` (mm/h acumulados na hora), além de fonte, estação, horário, longitude e latitude. Ausentes ficam vazios.
- GeoJSON: pontos `[longitude, latitude]`. No SIG, abrir GeoJSON ou importar CSV com X=longitude e Y=latitude; confirmar o referencial geográfico da fonte antes de reprojetar.
- CSV de previsão: estação/variável, hora de origem e prevista, horizonte, valor previsto e métricas. É separado das observações.

## Weather Underground / IALDEI10

O botão da estação pessoal requer `meteo_server.py` e a variável segura `WU_API_KEY`, autorizada para `api.weather.com`. Nunca coloque a chave no HTML, JavaScript, URL do dashboard, repositório ou chat. O endpoint local `/api/wu` consulta exclusivamente a estação IALDEI10 em unidades métricas, mantém cache por cinco minutos e não devolve a chave. O servidor escuta apenas em loopback; não é um servidor de produção exposto à Internet.

No GitHub Pages não há backend Python: o botão explica essa limitação. A integração autenticada só deve ser considerada validada depois de uma consulta com chave real. Uma leitura atual não basta para uma previsão: o histórico precisa acumular. O acumulado diário de chuva da PWS não é misturado com a precipitação horária IPMA.

## Verificar

```sh
node --test tests/meteo.test.mjs
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

Os testes incluem previsão linear e constante, comparação com persistência, insuficiência/lacunas, limites da humidade, ausentes, exportação, servidor e tratamento de erros sem divulgar a chave.

## Instalação e exportação independente

`bash install_meteo.sh` verifica Python e recolhe observações reais para `meteo-data/` (ignorado no Git). Não necessita de pacotes de terceiros. Pode definir `METEO_OUTPUT_DIR` para outro diretório. O exportador CLI também funciona sem abrir o mapa:

```sh
python3 -B tools/export_ipma.py --refresh --output meteo-data
```

Produz CSV separado por vírgula, CSV Excel separado por `;`, GeoJSON e manifesto de recolha. Cache de dez minutos; use `--station ID_IPMA` para filtrar uma estação. Não calcula previsões: estas pertencem à aplicação web. O `manifesto.json` inclui número de registos, estações e intervalo temporal. O script de instalação não deixa servidores em execução.

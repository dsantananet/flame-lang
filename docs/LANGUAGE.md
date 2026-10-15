# FlameLang — guia da versão experimental

Abra um exemplo no editor e clique em Executar. Os blocos usam indentação, com quatro espaços recomendados.

```flame
def dobro(n):
    return n * 2

for i in 1..5:
    if i > 3:
        print("Maior que três:", dobro(i))
    else:
        print(i)
```

Os intervalos incluem o último valor. Também são suportados `elif`, `and`, `or`, `not`, listas e índices.
Para CSV UTF-8 com cabeçalho `Concelho`, guardado na mesma pasta do programa:

```flame
load_csv("fwi.csv")
let valor = get("FWI", "Castelo Branco")
print(valor)
```

`load_csv` aceita vírgula, ponto e vírgula ou tabulação. `get` exige um único concelho e valor numérico.
`normalized_difference(a,b)` calcula `(a-b)/(a+b)` e rejeita denominador nulo. Pode ser usado para
demonstrar NDMI com NIR/SWIR e NDWI com as bandas apropriadas à definição escolhida; não processa imagens de satélite.
Não existe uma implementação de FWI meteorológico, nem simulação de propagação nesta versão.

Limites: 20000 passos, 32 chamadas aninhadas, CSV até 2 MB/10000 registos, saída até 100000 caracteres.
Imports, acesso a atributos Python, comandos do sistema e escrita de ficheiros pelos programas são rejeitados.
Só são lidos CSV sob a pasta do programa. Guarde os seus exemplos e dados fora da pasta da instalação.

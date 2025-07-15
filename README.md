
# 🔥 Flame — A Domain-Specific Language for Fire Modeling and Decision Support

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/dsantananet/flame-lang)
[![License](https://img.shields.io/github/license/dsantananet/flame-lang)](LICENSE)
[![Language](https://img.shields.io/badge/language-Python-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-0.1.0-orange)](https://github.com/dsantananet/flame-lang/releases)

---

## 🔍 O que é a Flame?

**Flame** é uma linguagem de programação específica de domínio (*DSL*) leve, expressiva e orientada à análise, simulação e apoio à decisão — especialmente desenvolvida para:
- **Modelação do comportamento do fogo**;
- **Risco meteorológico e ambiental**;
- **Suporte operacional em cenários críticos**.

A linguagem permite combinar lógica, dados meteorológicos, índices (ex: FWI, Haines, NDMI) e regras operacionais de forma simples e estruturada.

---

## 🚀 Instalação

```bash
git clone https://github.com/dsantananet/flame-lang.git
cd flame-lang
python interpreter.py script.flame
```

Requisitos:
- Python 3.10+
- (opcional) Bibliotecas: `pandas`, `numpy`, `shapely`, `geopandas`, `fpdf`

---

## 🧪 Exemplo de Código

```flame
if NDMI < 0.3 and PIR == "Muito Elevado" then
    alerta "🔥 Risco extremo de propagação"
end

if temperatura > 35 and vento > 30 then
    ativar "Plano de Reforço Operacional"
end
```

---

## 📁 Estrutura do Projeto

```bash
flame-lang/
├── interpreter.py         # Interpretador principal em Python
├── examples/              # Scripts Flame prontos a usar
├── img/                   # Ícones e logótipos
├── web/                   # Playground web (em desenvolvimento)
├── README.md
```

---

## 🧠 Casos de Utilização

- Apoio à decisão em sistemas de combate a incêndios.
- Simulação de regras meteorológicas personalizadas.
- Integração com dashboards operacionais.
- Ensino e formação em proteção civil e SIG.

---

## 🌍 Tópicos

`flame` · `programming-language` · `fire-modeling` · `wildfire` · `decision-support` · `dsl` · `environment` · `ai` · `open-source`

---

## 📜 Licença

Este projeto é distribuído sob a licença MIT.  
Consulta o ficheiro [LICENSE](LICENSE) para mais detalhes.

---

## 🧭 Desenvolvido por

**Daniel Ricardo Maranhão Santana**  
Especialista em Geointeligência, SIG, Proteção Civil e Comportamento do Fogo  
Castelo Branco, Portugal

---

## 🌐 Futuro

- 🔄 API REST para executar código Flame remotamente  
- 🧩 Integração com IA (PyTorch / scikit-learn)  
- 🛰️ Suporte a dados em tempo real (IPMA, SGIFR, FIRMS)  
- 🌍 Dashboard interativo (Streamlit / web)  
- 📘 Playground online para testes

---

## ⭐ Dá uma estrela se achaste útil!

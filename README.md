# 🔥 Flame Language

Flame is a lightweight scripting language created by **Daniel Ricardo Maranhão Santana**, designed for intuitive control of automation, fire risk evaluation, and data analysis — with clean syntax and rapid execution.

Developed under **Anternative 3** and supported by **Wareness**.

---

## 🚀 Quick Example

```flame
# Define a variable
let x = 10

# Print value
print("Value is", x)

# Function and loop
def square(n):
    return n * n

for i in 1..5:
    print(square(i))
```

---

## 🔥 Example Scripts

Explore real Flame programs in the [`examples/`](examples) folder:

- `hello.flame` – Simple variable and print  
- `squares.flame` – Loop and function example  
- `fire-risk.flame` – Fire risk evaluation with conditions  
- `fire-analysis.flame` – Advanced fire analysis with meteorology and FWI  
- `csv-fire-risk.flame` – Simulated CSV line-by-line fire risk evaluation  

---

## 📁 Sample CSV File

You can use this file as test input:

- [`dados_meteo.csv`](examples/dados_meteo.csv)

```csv
Concelho,Temp,Humidade,FWI
Proença-a-Nova,38,18,72
Castelo Branco,34,22,60
Sertã,40,15,80
```

---

## 🧠 Interpreter

A basic Python-based interpreter is included in [`flame_interpreter.py`](flame_interpreter.py).

### ▶️ Run via terminal:

```bash
python flame_interpreter.py
```

### 🧩 Or import and execute:

```python
from flame_interpreter import run_flame_code
run_flame_code(open("examples/hello.flame").read())
```

---

## 📘 Manual

The official Flame Manual is available as PDF:  
📥 [Download Manual](manual.pdf)

---

## 📄 Whitepaper

Explore the principles, design goals, and technical structure of Flame:  
📥 [Download Whitepaper](flame_whitepaper.pdf)

---

## 🌐 Website

Visit the official website:  
🌐 [https://dsantananet.github.io/flame-lang](https://dsantananet.github.io/flame-lang)

---

## 🛠️ Contribution

We welcome contributions!  
Fork this repository, clone it, and send a pull request with your improvements.

---

## 📜 License

MIT License — Free to use, modify and distribute.

---

**Institution:** Anternative 3  
**Supported by:** Wareness
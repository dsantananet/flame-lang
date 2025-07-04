# flame_interpreter.py
# Simple Flame interpreter (symbolic, partial)

def run_flame_code(code):
    variables = {}

    lines = code.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith("let "):
            # Variable assignment
            parts = line[4:].split("=", 1)
            var_name = parts[0].strip()
            value = eval(parts[1].strip(), {}, variables)
            variables[var_name] = value
        elif line.startswith("print("):
            # Handle print
            exec(line, {}, variables)
        elif line.startswith("#") or line == "":
            continue
        else:
            try:
                exec(line, {}, variables)
            except Exception as e:
                print("⚠️ Error:", e)

    return variables

# Example usage:
if __name__ == "__main__":
    flame_code = """
let x = 10
let y = x * 2
print("Value of y is", y)
"""
    run_flame_code(flame_code)
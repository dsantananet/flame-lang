import unittest, io, contextlib
from flame_interpreter import run_flame_code
class InterpreterTests(unittest.TestCase):
    def test_program(self):
        output=io.StringIO()
        with contextlib.redirect_stdout(output): result=run_flame_code('let name = "Daniel"\nlet x = 21\nprint("Hello", name, x * 2)')
        self.assertEqual(output.getvalue(),'Hello Daniel 42\n');self.assertEqual(result['x'],21)
    def test_rejects_python_execution(self):
        for code in ['import os', 'let x = __import__("os")', 'print(open("secret"))', 'let x = (1).__class__', 'let x = "a" * 1000000000']:
            with self.subTest(code=code), self.assertRaises(ValueError): run_flame_code(code)
    def test_error_line(self):
        with self.assertRaisesRegex(ValueError,'Linha 2'): run_flame_code('let x = 2\nprint(unknown)')
    def test_missing_variable_and_unsupported_syntax(self):
        for code in ['let x = missing', 'if x then', 'let x = 2 ** 999999']:
            with self.assertRaises(ValueError): run_flame_code(code)

    def test_conditions_loops_and_functions(self):
        code='def square(n):\n    return n * n\nlet total = 0\nfor i in 1..5:\n    let total = total + square(i)\nif total == 55 and not False:\n    print("ok")\nelse:\n    print("bad")'
        output=io.StringIO()
        with contextlib.redirect_stdout(output): result=run_flame_code(code)
        self.assertEqual(result['total'],55);self.assertEqual(output.getvalue(),'ok\n')

    def test_csv_and_path_boundary(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as directory:
            Path(directory,'data.csv').write_text('Concelho,Temp\nTeste,25\n',encoding='utf-8')
            result=run_flame_code('load_csv("data.csv")\nlet temperature = get("Temp", "Teste")',directory)
            self.assertEqual(result['temperature'],25)
            for filename in ('../data.csv','data.txt'):
                with self.assertRaises(ValueError):run_flame_code(f'load_csv("{filename}")',directory)

    def test_bounded_execution_and_recursion(self):
        for code in ['for i in 1..100000:\n    print(i)', 'def recurse(n):\n    return recurse(n)\nrecurse(1)', 'for i in 1..1000:\n    for j in 1..1000:\n        let x = i + j']:
            with self.assertRaises(ValueError):run_flame_code(code)

    def test_normalized_difference(self):
        self.assertAlmostEqual(run_flame_code('let ndmi = normalized_difference(0.6,0.2)')['ndmi'],0.5)
        with self.assertRaises(ValueError):run_flame_code('let x = normalized_difference(0,0)')

    def test_all_shipped_examples(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]/'examples'
        for path in root.glob('*.flame'):
            with self.subTest(path=path.name),contextlib.redirect_stdout(io.StringIO()):
                run_flame_code(path.read_text(encoding='utf-8-sig'),root)

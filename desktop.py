import sys
import io
import contextlib
from pathlib import Path
from flame_interpreter import run_flame_code

def self_test():
    output=io.StringIO()
    with contextlib.redirect_stdout(output): run_flame_code('let x = 21\nprint(x * 2)')
    assert output.getvalue()=='42\n'
    return 0

def main():
    import tkinter as tk
    from tkinter import filedialog, messagebox
    root=tk.Tk(); root.title('FlameLang · Editor experimental'); root.geometry('850x600')
    base_dir=Path(__file__).resolve().parent/'examples'
    tk.Label(root,text='FlameLang — editor e execução de programas',font=('Segoe UI',14)).pack(pady=12)
    code=tk.Text(root,font=('Consolas',12),height=17); code.pack(fill='both',expand=True,padx=16)
    code.insert('1.0','let nome = "Mundo"\nlet x = 21\nprint("Olá", nome)\nprint(x * 2)')
    bar=tk.Frame(root); bar.pack(pady=8)
    output=tk.Text(root,font=('Consolas',11),height=8); output.pack(fill='both',padx=16,pady=8)
    def run():
        capture=io.StringIO()
        try:
            with contextlib.redirect_stdout(capture): run_flame_code(code.get('1.0','end'),base_dir)
        except Exception as error: capture.write(str(error))
        output.delete('1.0','end'); output.insert('1.0',capture.getvalue())
    def load():
        nonlocal base_dir
        filename=filedialog.askopenfilename(initialdir=base_dir,filetypes=[('FlameLang','*.flame'),('Todos','*.*')])
        if filename:
            try:
                from pathlib import Path
                text=Path(filename).read_text(encoding='utf-8-sig'); base_dir=Path(filename).resolve().parent;code.delete('1.0','end');code.insert('1.0',text)
            except Exception as error: messagebox.showerror('Abrir',str(error))
    def save():
        nonlocal base_dir
        filename=filedialog.asksaveasfilename(defaultextension='.flame',filetypes=[('FlameLang','*.flame')])
        if filename:
            try:
                from pathlib import Path
                Path(filename).write_text(code.get('1.0','end-1c'),encoding='utf-8')
                base_dir=Path(filename).resolve().parent
            except Exception as error: messagebox.showerror('Guardar',str(error))
    for label,action in [('Abrir',load),('Guardar',save),('Executar',run)]: tk.Button(bar,text=label,command=action,width=15).pack(side='left',padx=5)
    root.mainloop()

if __name__=='__main__':
    if '--self-test' in sys.argv: sys.exit(self_test())
    main()

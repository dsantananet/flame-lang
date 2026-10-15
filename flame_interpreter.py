"""FlameLang: a bounded tree interpreter, without Python eval or exec."""
import ast
import csv
import math
import operator
import re
from pathlib import Path

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.Mod: operator.mod}

COMPARE = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
           ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge}

class Returned(Exception):
    def __init__(self,value): self.value=value

class Interpreter:
    def __init__(self,base_dir):
        self.base_dir=Path(base_dir).resolve(); self.steps=0;self.depth=0
        self.functions={};self.rows=[];self.output_size=0

    def tick(self):
        self.steps+=1
        if self.steps>20000: raise ValueError('Limite de execução atingido')

    def checked(self,value):
        if isinstance(value,int) and value.bit_length()>4096: raise ValueError('Número demasiado grande')
        if isinstance(value,float) and not math.isfinite(value): raise ValueError('Número não finito')
        if isinstance(value,(str,list,tuple)) and len(value)>10000: raise ValueError('Valor demasiado longo')
        return value

    def load_csv(self,filename):
        if not isinstance(filename,str): raise ValueError('Nome de ficheiro inválido')
        path=(self.base_dir/filename).resolve()
        if not path.is_relative_to(self.base_dir) or path.suffix.lower()!='.csv':
            raise ValueError('Só são permitidos CSV na pasta do programa')
        if path.stat().st_size>2_000_000: raise ValueError('CSV demasiado grande (máximo 2 MB)')
        with path.open(encoding='utf-8-sig',newline='') as stream:
            sample=stream.read(4096);stream.seek(0)
            try: dialect=csv.Sniffer().sniff(sample,delimiters=',;\t')
            except csv.Error: dialect=csv.excel
            reader=csv.DictReader(stream,dialect=dialect)
            rows=[]
            for row in reader:
                if len(rows)>=10000: raise ValueError('CSV excede 10000 linhas')
                rows.append(row)
        self.rows=rows
        return len(rows)

    def get(self,column,place):
        matches=[row for row in self.rows if row.get('Concelho','').casefold()==str(place).casefold()]
        if len(matches)!=1: raise ValueError('Concelho ausente ou duplicado')
        value=matches[0].get(column)
        if value is None or not value.strip(): raise ValueError('Campo ausente')
        return self.checked(float(value.replace(',','.')))

    def call(self,node,variables):
        if node.keywords: raise ValueError('Argumentos nomeados não suportados')
        args=[self.visit(arg,variables) for arg in node.args]
        if isinstance(node.func,ast.Attribute):
            value=self.visit(node.func.value,variables)
            if node.func.attr=='split' and isinstance(value,str) and len(args)==1 and isinstance(args[0],str):
                return self.checked(value.split(args[0]))
            raise ValueError('Método não permitido')
        if not isinstance(node.func,ast.Name): raise ValueError('Chamada não permitida')
        name=node.func.id
        if name=='print':
            text=' '.join(str(arg) for arg in args);self.output_size+=len(text)+1
            if self.output_size>100000: raise ValueError('Limite de saída atingido')
            print(text);return None
        if name=='load_csv' and len(args)==1:return self.load_csv(*args)
        if name=='get' and len(args)==2:return self.get(*args)
        if name=='len' and len(args)==1 and isinstance(args[0],(str,list,tuple,range)):return len(args[0])
        if name=='to_number' and len(args)==1:return self.checked(float(args[0]))
        if name=='inclusive_range' and len(args)==2 and all(type(v) is int for v in args):
            if abs(args[1]-args[0])>10000:raise ValueError('Ciclo demasiado longo')
            return range(args[0],args[1]+1)
        if name=='normalized_difference' and len(args)==2 and all(type(v) in (int,float) for v in args):
            if args[0]+args[1]==0:raise ValueError('Denominador nulo no índice normalizado')
            return self.checked((args[0]-args[1])/(args[0]+args[1]))
        if name in self.functions:
            function=self.functions[name]
            if len(args)!=len(function.args.args):raise ValueError('Número incorreto de argumentos')
            if self.depth>=32:raise ValueError('Limite de chamadas atingido')
            scope=dict(variables);scope.update(zip((a.arg for a in function.args.args),args))
            self.depth+=1
            try:
                self.block(function.body,scope)
            except Returned as result:return result.value
            finally:self.depth-=1
            return None
        raise ValueError('Função não permitida: '+name)

    def visit(self,node,variables):
        self.tick()
        if isinstance(node, ast.Constant) and type(node.value) in (str,int,float,bool):
            return self.checked(node.value)
        if isinstance(node, ast.Name) and node.id in variables: return variables[node.id]
        if isinstance(node,ast.List):return self.checked([self.visit(value,variables) for value in node.elts])
        if isinstance(node,ast.Subscript):
            value=self.visit(node.value,variables);index=self.visit(node.slice,variables)
            if not isinstance(value,(str,list,tuple)) or type(index) is not int:raise ValueError('Índice inválido')
            return value[index]
        if isinstance(node,ast.Call):return self.call(node,variables)
        if isinstance(node,ast.BoolOp):
            for part in node.values:
                value=self.visit(part,variables)
                if isinstance(node.op,ast.And) and not value:return value
                if isinstance(node.op,ast.Or) and value:return value
            return value
        if isinstance(node,ast.Compare):
            left=self.visit(node.left,variables)
            for op,right_node in zip(node.ops,node.comparators):
                if type(op) not in COMPARE:raise ValueError('Comparação não suportada')
                right=self.visit(right_node,variables)
                if not COMPARE[type(op)](left,right):return False
                left=right
            return True
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.Not):return not self.visit(node.operand,variables)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            value=self.visit(node.operand,variables)
            if type(value) not in (int,float): raise ValueError('Esperado número')
            return value if isinstance(node.op,ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            a,b=self.visit(node.left,variables),self.visit(node.right,variables)
            if type(a) not in (int,float) or type(b) not in (int,float):
                if isinstance(node.op,ast.Add) and type(a) is str and type(b) is str:
                    if len(a)+len(b)>10000: raise ValueError('Texto demasiado longo')
                    return a+b
                raise ValueError('Operação requer números')
            result=OPS[type(node.op)](a,b)
            return self.checked(result)
        raise ValueError('Expressão não suportada')

    def block(self,nodes,variables):
        for node in nodes:
            self.tick()
            try:
                if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
                    variables[node.targets[0].id]=self.visit(node.value,variables)
                elif isinstance(node,ast.Expr) and isinstance(node.value,ast.Call):self.call(node.value,variables)
                elif isinstance(node,ast.If):self.block(node.body if self.visit(node.test,variables) else node.orelse,variables)
                elif isinstance(node,ast.For) and isinstance(node.target,ast.Name) and not node.orelse:
                    values=self.visit(node.iter,variables)
                    if not isinstance(values,(list,tuple,range)):raise ValueError('Ciclo requer lista ou intervalo')
                    for value in values:
                        self.tick();variables[node.target.id]=value;self.block(node.body,variables)
                elif isinstance(node,ast.FunctionDef):
                    a=node.args
                    if node.decorator_list or a.defaults or a.kw_defaults or a.kwonlyargs or a.vararg or a.kwarg or a.posonlyargs or node.returns or any(arg.annotation for arg in a.args):
                        raise ValueError('Definição de função não suportada')
                    self.functions[node.name]=node
                elif isinstance(node,ast.Return) and self.depth:raise Returned(self.visit(node.value,variables) if node.value else None)
                else:raise ValueError('Instrução não suportada')
            except Returned:raise
            except Exception as error:
                if isinstance(error,ValueError) and str(error).startswith('Linha '):raise
                raise ValueError(f'Linha {node.lineno}: {error}') from error

def run_flame_code(code,base_dir=None):
    if len(code)>100000: raise ValueError('Programa demasiado longo')
    translated=[]
    for line in code.splitlines():
        line=re.sub(r'^(\s*)let\s+',r'\1',line)
        match=re.fullmatch(r'(\s*)for\s+([A-Za-z_]\w*)\s+in\s+(.+?)\.\.(.+):\s*',line)
        if match:line=f'{match[1]}for {match[2]} in inclusive_range({match[3]}, {match[4]}):'
        translated.append(line)
    try:tree=ast.parse('\n'.join(translated))
    except SyntaxError as error:raise ValueError(f'Linha {error.lineno}: sintaxe inválida') from error
    if sum(1 for _ in ast.walk(tree))>5000:raise ValueError('Programa demasiado complexo')
    variables={}
    Interpreter(base_dir or Path.cwd()).block(tree.body,variables)
    return variables

if __name__=='__main__':
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('script',type=Path)
    args=parser.parse_args()
    try: run_flame_code(args.script.read_text(encoding='utf-8-sig'),args.script.resolve().parent)
    except (OSError,ValueError) as error: parser.exit(1,str(error)+'\n')

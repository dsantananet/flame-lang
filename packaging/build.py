import subprocess,sys,tempfile,os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
args=[sys.executable,'-m','PyInstaller','--noconfirm','--windowed','--workpath',tempfile.mkdtemp(prefix='flame-build-'),'--distpath',os.environ.get('BUILD_OUTPUT','dist-current'),'--name','FlameLang','--icon','packaging/app.ico']

args+=['desktop.py']
args+=['--add-data','examples:examples']
subprocess.run(args,cwd=root,check=True)

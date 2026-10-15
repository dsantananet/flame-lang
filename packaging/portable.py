from pathlib import Path
import shutil,hashlib
root=Path(__file__).resolve().parents[1]
bundle=root/'dist-current'/'FlameLang'
release=root/'release';release.mkdir(exist_ok=True)
for file in ['LEIA-ME.txt','LEGAL-NOTICE.md','LICENSE']:
    shutil.copy2(root/file,bundle/file)
shutil.copy2(root/'LEIA-ME.txt',release/'LEIA-ME.txt')
shutil.make_archive(str(release/'FlameLang-0.2.0-rc.1-windows-x64-portable'),'zip',bundle)
files=sorted(p for p in release.iterdir() if p.suffix in ('.exe','.zip','.txt') and p.name!='SHA256SUMS.txt')
(release/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files),encoding='utf-8')

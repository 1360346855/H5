from pathlib import Path,PurePosixPath
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json,shutil
m=json.loads(Path('presentation/history-manifest.json').read_text());out=Path('release');out.mkdir(exist_ok=True)
def check(data,spec):
 assert len(data)==spec['size']
 assert hashlib.sha256(data).hexdigest()==spec['sha256']
 return data
archive=out/'Curious_Version_History.zip'
with archive.open('wb') as f:
 for part in m['parts']:f.write(check(Path(part['path']).read_bytes(),part))
check(archive.read_bytes(),m)
with ZipFile(archive) as z:
 assert z.testzip() is None
 assert set(z.namelist())==set(m['members'])
 for name in z.namelist():
  parts=PurePosixPath(name).parts
  assert parts[0]=='history' and '..' not in parts and not name.startswith('/')
  data=check(z.read(name),m['members'][name]);path=Path(name);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
for v in range(1,125):
 assert Path(f'history/v{v:03d}.md').is_file()
 assert Path(f'history/screens/v{v:03d}-home.jpg').is_file()
# Preserve the index filter even when card display styles override the hidden attribute.
index=Path('history/index.html');index.write_text(index.read_text().replace('.card{display:block', '[hidden]{display:none!important}.card{display:block'))
with ZipFile(archive,'w',ZIP_DEFLATED) as z:
 for file in Path('history').rglob('*'):
  if file.is_file():z.write(file,file.as_posix())
with ZipFile(archive) as z:assert z.testzip() is None
for name in ['Curious_Latest_QR.png','Curious_Latest_QR.svg','Curious_Versions.csv']:shutil.copy2(Path('history')/name,out/name)
print('All 124 version links and source-restored screenshots verified')

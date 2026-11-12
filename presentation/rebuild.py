import hashlib, json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

def checked(data, spec):
    assert len(data) == spec['size']
    assert hashlib.sha256(data).hexdigest() == spec['sha256']
    return data

manifest = json.loads(Path('presentation/manifest.json').read_text())
out = Path('release'); out.mkdir(exist_ok=True)
payload = out/'payload.zip'
with payload.open('wb') as f:
    for part in manifest['parts']:
        f.write(checked(Path(part['path']).read_bytes(), part))
assert payload.stat().st_size == manifest['payload_size']
assert hashlib.sha256(payload.read_bytes()).hexdigest() == manifest['payload_sha256']
base_meta = json.loads(Path('bundle/manifest.json').read_text())
base = out/'base.zip'
with base.open('wb') as f:
    for part in base_meta['parts']:
        f.write(checked(Path(part['path']).read_bytes(), part))
assert hashlib.sha256(base.read_bytes()).hexdigest() == base_meta['sha256']
deck = out/manifest['filename']
with ZipFile(payload) as source, ZipFile(base) as assets, ZipFile(deck, 'w', ZIP_DEFLATED) as target:
    for info in source.infolist():
        target.writestr(info, source.read(info.filename))
    for media in manifest['external_media']:
        target.writestr(media['target'], checked(assets.read(media['source']), media))
with ZipFile(deck) as z:
    assert z.testzip() is None
    assert set(z.namelist()) == set(manifest['members'])
    for name, spec in manifest['members'].items():
        checked(z.read(name), spec)
with ZipFile(out/'Curious_Project_Presentation_Iteration.zip', 'w', ZIP_DEFLATED) as z:
    z.write(deck, deck.name)
print('Verified editable presentation:', deck.stat().st_size, 'bytes')

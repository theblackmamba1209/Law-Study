import sys, subprocess, os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
pdf, out, rot = sys.argv[1], sys.argv[2], int(sys.argv[3])
dpi = sys.argv[4] if len(sys.argv) > 4 else '200'
os.makedirs(out, exist_ok=True)
n = int([l.split()[1] for l in subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout.splitlines() if l.startswith('Pages:')][0])
def do(p):
    base = os.path.join(out, f"p{p:03d}")
    if os.path.exists(base + ".done"): return
    subprocess.run(['pdftoppm', '-f', str(p), '-l', str(p), '-r', dpi, '-gray', '-png', '-singlefile', pdf, base], check=True)
    im = Image.open(base + '.png')
    if rot: im = im.rotate(rot, expand=True)
    w, h = im.size
    parts = [im] if h >= w else [im.crop((0, 0, w // 2, h)), im.crop((w // 2, 0, w, h))]
    txt = []
    for i, part in enumerate(parts):
        fn = f"{base}_{i}.png"; part.save(fn)
        r = subprocess.run(['tesseract', fn, '-', '-l', 'eng', '--psm', '6'], capture_output=True, text=True, env={**os.environ, 'OMP_THREAD_LIMIT': '1'})
        txt.append(r.stdout); os.remove(fn)
    open(base + '.txt', 'w').write('\n\f\n'.join(txt))
    os.remove(base + '.png'); open(base + '.done', 'w').write('')
with ThreadPoolExecutor(2) as ex: list(ex.map(do, range(1, n + 1)))
print('DONE', pdf)

#!/usr/bin/env python3
"""deliver.py - 打包一轮练习的全部交付物：PNG + 对比图 + .drawio。

用法: python3 scripts/deliver.py <round_dir> [--pairs ref.png:mine.png:name ...]
      或 python3 scripts/deliver.py <round_dir> --auto

--auto 模式：自动配对 round_dir 下的 ref-*.{png,jpg} 与 p3-*.png
对比图统一输出到 <round_dir>/compare/对比-<名称>-<时间戳>.png
最后打印全部交付物清单（PNG / 对比图 / drawio），直接复制发给用户。
"""
import os, sys, time, glob
from PIL import Image, ImageDraw, ImageFont

W = 1200
def load_font(size=28):
    for p in ['/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def compare(ref_path, mine_path, name, outdir, ts, font):
    r = Image.open(ref_path).convert('RGB')
    m = Image.open(mine_path).convert('RGB')
    def fit(im):
        rt = W / im.width
        return im.resize((W, int(im.height * rt)), Image.LANCZOS)
    r, m = fit(r), fit(m)
    lh = 55
    canvas = Image.new('RGB', (W, lh + r.height + 15 + lh + m.height), 'white')
    d = ImageDraw.Draw(canvas)
    d.text((15, 10), f'原图参考（{name}）', fill='black', font=font)
    canvas.paste(r, (0, lh))
    y2 = lh + r.height + 15
    d.text((15, y2 + 10), f'Muse 重绘（{name}）', fill='black', font=font)
    canvas.paste(m, (0, y2 + lh))
    out = f'{outdir}/对比-{name}-{ts}.png'
    canvas.save(out)
    return out

def main():
    if len(sys.argv) < 2:
        print('用法: deliver.py <round_dir> [--auto]')
        sys.exit(1)
    rd = sys.argv[1].rstrip('/')
    auto = '--auto' in sys.argv
    ts = time.strftime('%H%M%S')
    font = load_font()
    outdir = f'{rd}/compare'
    os.makedirs(outdir, exist_ok=True)

    pairs = []
    if auto:
        # ref-*.png/jpg 按文件名排序，mine = p3-*.png 按时间排序
        refs = sorted(glob.glob(f'{rd}/ref-*.png') + glob.glob(f'{rd}/ref-*.jpg'))
        mines = sorted(glob.glob(f'{rd}/p3-*.png'), key=os.path.getmtime)
        for ref, mine in zip(refs, mines):
            base = os.path.basename(ref)
            name = base.replace('ref-', '').rsplit('.', 1)[0]
            pairs.append((ref, mine, name))
    else:
        for arg in sys.argv[2:]:
            if ':' in arg:
                r, mi, n = arg.split(':', 2)
                pairs.append((f'{rd}/{r}', f'{rd}/{mi}', n))

    comparisons = []
    for ref, mine, name in pairs:
        if not os.path.exists(ref):
            print(f'WARN 跳过 {name}：缺 {ref}')
            continue
        if not os.path.exists(mine):
            print(f'WARN 跳过 {name}：缺 {mine}')
            continue
        comparisons.append(compare(ref, mine, name, outdir, ts, font))

    drawios = sorted(glob.glob(f'{rd}/*.drawio'))
    pngs = sorted(glob.glob(f'{rd}/p3-*.png'))

    print(f'\n=== 交付清单（时间戳 {ts}）===')
    print(f'\n-- 重绘 PNG（{len(pngs)}）--')
    for p in pngs: print(f'  {p}')
    print(f'\n-- 对比图（{len(comparisons)}）--')
    for c in comparisons: print(f'  {c}')
    print(f'\n-- .drawio（{len(drawios)}）--')
    for d in drawios: print(f'  {d}')
    print('\n全部打包完毕，直接发给用户。')

if __name__ == '__main__':
    main()

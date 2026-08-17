#!/usr/bin/env python3
"""
Build preview/ -- the minimal re-skin of the app.

Only the stylesheet and a little copy change; the whole application script is
copied across untouched, so the preview behaves exactly like the live app.
Palette: bone ground, warm ink, one lilac accent. No greens.
"""

import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview")

CSS = """
:root{
  --bg:#F7F5F1;        /* bone -- page ground */
  --card:#FFFFFF;      /* paper -- cards, sheets */
  --txt:#191716;       /* warm ink -- text and primary buttons */
  --dim:#79706A;       /* warm grey -- secondary text */
  --line:#E6E0D8;      /* hairline */
  --volt:#5B4DD1;      /* lilac -- the single accent */
  --halo:#ECE8FB;      /* lilac tint -- badges, exit pass */
  --warn:#B85A50;      /* clay -- errors */
  --r:14px;
}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Helvetica Neue",Inter,Arial,sans-serif;
  background:#EBE7E0; color:var(--txt); -webkit-font-smoothing:antialiased;
  display:flex; justify-content:center;
}
#app{width:100%; max-width:430px; min-height:100dvh; background:var(--bg); display:flex; flex-direction:column; position:relative}
@media(min-width:480px){
  body{padding:28px 0}
  #app{min-height:calc(100dvh - 56px); border:1px solid var(--line); box-shadow:0 16px 44px rgba(25,23,22,.10)}
}

.up{text-transform:uppercase; letter-spacing:.1em}
.big{font-weight:600; letter-spacing:-.015em; text-transform:none}
.dim{color:var(--dim)}
.price{font-variant-numeric:tabular-nums}

header{display:flex; align-items:center; justify-content:space-between; padding:18px 20px; border-bottom:1px solid var(--line); position:sticky; top:0; background:var(--bg); z-index:5}
.mark{width:13px;height:13px;background:var(--volt);border-radius:4px}
.wordmark{font-size:19px; font-weight:600; letter-spacing:.16em}
#storebtn{background:transparent;border:0;font:inherit;font-size:11px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);cursor:pointer;padding:6px 0}

main{flex:1; overflow-y:auto; padding-bottom:100px}
.screen{display:none}
.screen.on{display:block}

.btn{
  display:block; width:100%; padding:16px; font:inherit; font-size:15px; font-weight:600;
  cursor:pointer; text-align:center; transition:opacity .15s ease;
  background:var(--txt); color:#FBFAF8; border:1px solid var(--txt); border-radius:var(--r);
}
.btn.ghost{background:transparent; color:var(--txt); border-color:var(--line)}
.btn.mono{background:var(--volt); border-color:var(--volt); color:#fff}
.btn+.btn{margin-top:10px}
.btn:active{opacity:.82}
button:focus-visible,a:focus-visible,input:focus-visible{outline:2px solid var(--volt); outline-offset:2px}
.btn[disabled]{opacity:.35; cursor:default}

.pad{padding:18px 20px}
.hero{padding:30px 20px 4px}
.hero h1{font-size:33px; font-weight:600; letter-spacing:-.025em; line-height:1.14; text-wrap:balance}
.hero p{margin-top:14px; font-size:14px; color:var(--dim); line-height:1.65; max-width:35ch}

.viewfinder{margin:20px; height:278px; background:#E3DED6; border:1px solid var(--line); border-radius:18px; display:flex; align-items:center; justify-content:center; position:relative; overflow:hidden}
#vid{position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:none}
#vid.on{display:block}
.reticle{width:206px; height:118px; border:2px solid #fff; border-radius:12px; position:relative; z-index:2; box-shadow:0 0 0 1px rgba(25,23,22,.22), 0 2px 10px rgba(25,23,22,.18)}
.hint{position:absolute; bottom:14px; z-index:2; font-size:10px; letter-spacing:.12em; text-transform:uppercase; font-weight:600; color:#F7F5F1; background:rgba(25,23,22,.72); padding:6px 12px; border-radius:999px}
#torch{position:absolute; top:12px; right:12px; z-index:3; display:none; background:rgba(25,23,22,.72); border:0; color:#F7F5F1; font:inherit; font-size:10px; font-weight:600; letter-spacing:.12em; text-transform:uppercase; padding:8px 12px; cursor:pointer; border-radius:999px}
#torch.on{display:block}

.toast{margin:0 20px 6px; padding:14px 16px; background:var(--halo); border:1px solid #D8D0F4; color:var(--txt); font-size:13.5px; display:none; justify-content:space-between; gap:10px; border-radius:12px}
.toast.on{display:flex}
.toast.bad{background:#FAEBE9; border-color:#EFD1CC; color:var(--warn)}

.field{display:flex; gap:10px; padding:0 20px 6px}
.field input{flex:1; min-width:0; padding:15px; font:inherit; font-size:15px; background:var(--card); border:1px solid var(--line); color:var(--txt); border-radius:12px}
.field input::placeholder{color:var(--dim); text-transform:none; font-size:15px; letter-spacing:0}
.field button{padding:0 20px; font:inherit; font-size:14px; font-weight:600; background:var(--txt); border:1px solid var(--txt); color:#FBFAF8; cursor:pointer; border-radius:12px}

.rows{padding:0 20px}
.row{display:flex; justify-content:space-between; gap:12px; padding:18px 0; border-bottom:1px solid var(--line)}
.row .nm{font-size:15px; font-weight:600; letter-spacing:0}
.row .sub{font-size:13px; color:var(--dim); margin-top:4px}
.qty{display:flex; align-items:center; gap:14px; margin-top:12px}
.qty button{width:30px;height:30px;border:1px solid var(--line);background:var(--card);color:var(--txt);font:inherit;font-size:15px;font-weight:600;cursor:pointer;border-radius:999px;line-height:1}
.qty span{font-size:14px; min-width:16px; text-align:center; font-weight:600; font-variant-numeric:tabular-nums}
.totalline{display:flex; justify-content:space-between; align-items:baseline; padding:22px 20px 4px}
.totalline .amt{font-size:31px; font-weight:600; letter-spacing:-.02em}
.empty{padding:64px 20px; text-align:center; color:var(--dim); font-size:14px; line-height:1.8; text-transform:none; letter-spacing:0}

.sheetwrap{position:fixed; inset:0; background:rgba(25,23,22,.42); display:none; align-items:flex-end; justify-content:center; z-index:20}
.sheetwrap.on{display:flex}
.sheet{width:100%; max-width:430px; max-height:92dvh; overflow-y:auto; background:var(--card); border-radius:22px 22px 0 0; padding:26px 20px 34px; box-shadow:0 -10px 40px rgba(25,23,22,.16)}
#payqr{background:#fff; padding:12px; width:200px; margin:18px auto; border:1px solid var(--line); border-radius:14px; display:flex; align-items:center; justify-content:center; min-height:200px}
#payqr img{display:block; width:176px; height:176px; image-rendering:pixelated}

.lbl2{display:block; font-size:10.5px; font-weight:600; letter-spacing:.13em; text-transform:uppercase; color:var(--dim); margin:18px 0 7px}
.sheet input[type=text]{width:100%; padding:15px; font:inherit; font-size:15px; background:var(--bg); border:1px solid var(--line); color:var(--txt); border-radius:12px}
.err{color:var(--warn); font-size:12.5px; margin-top:8px; display:none}
.err.on{display:block}

/* exit pass */
#pass{position:fixed; inset:0; background:var(--halo); color:var(--txt); z-index:30; display:none; flex-direction:column; align-items:center; justify-content:flex-start; text-align:center; padding:38px 26px 30px; overflow-y:auto}
#pass.on{display:flex}
#pass .lbl{font-size:10.5px; font-weight:600; letter-spacing:.14em; text-transform:uppercase; color:rgba(25,23,22,.55)}
#pass .count{font-size:62px; font-weight:600; line-height:1; margin:12px 0 4px; letter-spacing:-.03em}
#qrtile{background:#fff; padding:14px; border-radius:16px; margin:20px 0 12px; min-width:192px; min-height:192px; display:flex; align-items:center; justify-content:center; border:1px solid rgba(25,23,22,.10)}
#qrtile img{display:block; width:168px; height:168px; image-rendering:pixelated}
#pass .code{font-size:15px; font-weight:600; letter-spacing:.18em; text-transform:uppercase; margin:4px 0 12px; color:var(--volt)}
#drain{width:180px; height:3px; background:rgba(25,23,22,.12); overflow:hidden; border-radius:999px}
#drain i{display:block; height:100%; background:var(--volt); transform-origin:left}
#pass .items{margin-top:20px; font-size:13px; font-weight:500; line-height:1.9; color:rgba(25,23,22,.72)}
#pass .btn{max-width:300px; margin-top:26px; background:var(--txt); border-color:var(--txt); color:#FBFAF8}

.wrow{padding:18px 20px; border-bottom:1px solid var(--line)}
.wrow .dt{font-size:10.5px; letter-spacing:.12em; text-transform:uppercase; color:var(--dim); margin-bottom:8px}
.wacts{display:flex; gap:10px; margin-top:14px}
.wacts button{flex:1; padding:10px; font:inherit; font-size:12.5px; font-weight:600; background:var(--card); border:1px solid var(--line); color:var(--txt); cursor:pointer; border-radius:999px}

nav{position:fixed; bottom:0; left:50%; transform:translateX(-50%); width:100%; max-width:430px; background:rgba(247,245,241,.94); -webkit-backdrop-filter:blur(12px); backdrop-filter:blur(12px); border-top:1px solid var(--line); display:flex; z-index:10; padding-bottom:env(safe-area-inset-bottom)}
nav button{flex:1; padding:15px 0 17px; background:transparent; border:0; font:inherit; cursor:pointer; font-size:12.5px; font-weight:600; letter-spacing:0; color:var(--dim); position:relative}
nav button.on{color:var(--txt)}
nav button.on::after{content:""; position:absolute; bottom:8px; left:50%; transform:translateX(-50%); width:5px; height:5px; border-radius:999px; background:var(--volt)}
#bagdot[hidden]{display:none}
#bagdot{display:inline-block; min-width:18px; padding:2px 6px; font-size:10.5px; background:var(--volt); color:#fff; border-radius:999px; margin-left:5px; letter-spacing:0}
.note{font-size:12px; color:var(--dim); line-height:1.7; padding:14px 20px}
.note b{color:var(--txt); font-weight:600}
.note a{color:var(--volt)}
.banner{margin:0 20px 8px; padding:13px 15px; background:#FAEBE9; border:1px solid #EFD1CC; color:var(--warn); font-size:12.5px; line-height:1.6; border-radius:12px; display:none}
.banner.on{display:block}
"""


def build_app():
    src = io.open(os.path.join(HERE, "index.html"), encoding="utf-8").read()

    # 1. swap the stylesheet wholesale
    out, n = re.subn(r"(?s)<style>.*?</style>", "<style>" + CSS + "</style>", src, count=1)
    assert n == 1, "stylesheet not found"

    # 2. the scrolling marquee is the opposite of minimal
    out, n = re.subn(r'(?s)\s*<div class="ticker".*?</div>\n', "\n", out, count=1)
    assert n == 1, "ticker not found"

    # 3. browser chrome should match the bone ground
    out = out.replace('<meta name="theme-color" content="#0E0E0E">',
                      '<meta name="theme-color" content="#F7F5F1">')

    # 4. vault item names are uppercased by an inline style in the render code
    out = out.replace('font-weight:700;text-transform:uppercase;letter-spacing:.04em',
                      'font-weight:600;letter-spacing:0')

    # 5. shouty copy -> plain
    out = out.replace('toast("ADDED — "+p.nm.toUpperCase()', 'toast("Added — "+p.nm')
    out = out.replace('toast("NOT IN STORE — "+v', 'toast("Not in this store — "+v')
    out = out.replace('toast("NOT IN STORE — "+raw', 'toast("Not in this store — "+raw')
    out = out.replace("Bag's empty.<br>Go scan something.", "Your bag is empty.<br>Go scan something.")
    out = out.replace("Everything you cop<br>lands here.", "Everything you buy<br>lands here.")

    os.makedirs(OUT, exist_ok=True)
    io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="").write(out)
    print("preview/index.html written")


def build_tags():
    src = io.open(os.path.join(HERE, "tags.html"), encoding="utf-8").read()
    src = src.replace("--volt:#D8FF3E", "--volt:#ECE8FB")
    src = src.replace("background:#F2F2F2", "background:#F7F5F1")
    src = src.replace("border:2px solid #000", "border:1px solid #E6E0D8")
    src = src.replace(".tag .brand{display:inline-block;background:var(--volt);",
                      ".tag .brand{display:inline-block;background:var(--volt);color:#5B4DD1;border-radius:999px;")
    io.open(os.path.join(OUT, "tags.html"), "w", encoding="utf-8", newline="").write(src)
    print("preview/tags.html written")


if __name__ == "__main__":
    build_app()
    build_tags()

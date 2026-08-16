#!/usr/bin/env python3
"""
Build the shareable, self-contained versions of the app and the test tags.

Claude Artifacts block every external request, so the two CDN libraries have to
be inlined. Run this after editing index.html / tags.html, then re-publish:

    python build_artifact.py

Outputs build/app.html and build/tags.html -- page fragments (no <html>/<head>/
<body>), which is what the Artifact publisher expects.

The libraries are cached in build/vendor/ on first run.
"""

import io
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
VENDOR = os.path.join(BUILD, "vendor")

LIBS = {
    "qrcode.min.js": "https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js",
    "zxing.min.js": "https://cdn.jsdelivr.net/npm/@zxing/browser@0.1.5/umd/zxing-browser.min.js",
}

# Link to the published tags artifact, shown inside the app. Update after publishing.
TAGS_URL = "https://claude.ai/code/artifact/a11063ee-ebce-41fc-b0e8-4a0f1193f4d2"


def read(path):
    return io.open(path, encoding="utf-8").read()


def write(path, text):
    io.open(path, "w", encoding="utf-8", newline="").write(text)


def vendor(name):
    path = os.path.join(VENDOR, name)
    if not os.path.exists(path):
        os.makedirs(VENDOR, exist_ok=True)
        print("fetching " + name)
        with urllib.request.urlopen(LIBS[name]) as r:
            write(path, r.read().decode("utf-8"))
    src = read(path)
    # a literal </script> inside a library would close our inline block early
    return src.replace("</script", "<\\/script")


def strip_shell(html):
    """Drop the document wrapper; the publisher supplies its own."""
    html = re.sub(r"(?is)^.*?<head>", "", html)
    html = re.sub(r"(?is)</head>\s*<body>", "", html)
    html = re.sub(r"(?is)</body>\s*</html>\s*$", "", html)
    html = re.sub(r'(?i)\s*<meta[^>]*>\s*\n', "", html)
    return html.strip() + "\n"


def build_app():
    html = strip_shell(read(os.path.join(HERE, "index.html")))

    for name in ("qrcode.min.js", "zxing.min.js"):
        url = LIBS[name]
        tag = '<script src="%s"></script>' % url
        assert tag in html, "could not find the script tag for " + name
        html = html.replace(tag, "<script>\n" + vendor(name) + "\n</script>")

    # copy that only makes sense when the files are served locally
    html = html.replace(
        'Open the <a href="tags.html" target="_blank" rel="noopener" style="color:var(--volt)">test tags</a> on a second screen for real, scannable barcodes.',
        'Open the <a href="%s" target="_blank" rel="noopener" style="color:var(--volt)">test tags</a> '
        'on a second screen for real, scannable barcodes.' % TAGS_URL)
    html = html.replace(
        "run serve.py and open the https link.",
        "open this page as its own tab rather than inside another app.")
    html = html.replace(
        "Run serve.py in this folder and open the https:// link it prints.",
        "Open the shared link over https instead.")

    # inside an embed the camera is blocked no matter what the user allows
    html = html.replace(
        "/* secure-context warning up front */",
        """/* embedded pages cannot get the camera -- say so instead of blaming permissions */
if(window.self!==window.top){
  var eb=el("httpsbanner");
  eb.textContent="This page is embedded, so the browser will not hand over the camera. Open the link in its own browser tab to scan. Typing a code works here.";
  eb.classList.add("on");
}

/* secure-context warning up front */""")

    os.makedirs(BUILD, exist_ok=True)
    out = os.path.join(BUILD, "app.html")
    write(out, html)
    print("wrote %s (%.0f KB)" % (out, os.path.getsize(out) / 1024))


def build_tags():
    html = strip_shell(read(os.path.join(HERE, "tags.html")))
    os.makedirs(BUILD, exist_ok=True)
    out = os.path.join(BUILD, "tags.html")
    write(out, html)
    print("wrote %s (%.0f KB)" % (out, os.path.getsize(out) / 1024))


if __name__ == "__main__":
    build_tags()
    build_app()

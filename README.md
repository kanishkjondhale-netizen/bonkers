# BONKERS — scan, pay, walk out

A single-file store prototype: scan hangtags with the phone camera, pay by UPI, show an
exit pass at the door. No accounts, no backend.

```
bonkers/
  index.html   the app
  tags.html    printable test hangtags with real EAN-13 barcodes
  serve.py     local https server so the camera is allowed to start
```

## Run it

```bash
python serve.py
```

It prints two URLs. Open the `192.168.x.x` one **on the phone** (same wifi). The cert is
self-signed, so the browser warns once — Chrome: *Advanced → Proceed*, Safari: *Show
details → visit this website*. After that the camera works.

On the laptop, `https://localhost:8443/` also works, as does plain `python serve.py --http`
(camera is allowed on `localhost` even over http).

Opening `index.html` by double-clicking it will **not** give you a camera — browsers block
`getUserMedia` on `file://`. The app says so in a banner and still lets you simulate or
type codes.

## First run

The app asks for a **UPI ID** on first open (header ⚙ reopens it any time). Payments go to
that VPA. Until it is set, the pay button says so and cannot start a payment.

## Testing a scan

Open `tags.html` on a laptop or second phone — six real EAN-13 barcodes matching the
catalogue. Point the app's camera at one. Bright screen, 10–20 cm away. All six decode as
valid EAN-13.

No second screen? Type `8902000000016` into the barcode box, or hit **Simulate a scan**.

## What is real and what is faked

Real: camera scanning (BarcodeDetector where available, ZXing everywhere else), the bag and
its maths, the UPI intent link and its QR, the exit pass, and persistence across reloads
(everything is in `localStorage` on the device).

Faked: **payment confirmation**. Tapping *I've paid* is taken at its word — there is no
server checking that money actually arrived, so the exit pass proves nothing. The door QR
also just rotates a random token; no one is verifying it. For a real store both need a
backend: a Razorpay/Cashfree order with a server-side webhook, and a signed, server-issued
pass the door scanner validates.

## Changing the catalogue

Edit `CATALOG` near the top of the script in `index.html` — `ean` is the barcode the scanner
matches, `pr` is rupees. Mirror the same list in `tags.html` if you want printable tags for
it. EAN-13 codes need a valid check digit; `tags.html` marks a bad one with ✕ instead of
silently printing an unscannable barcode.

## Shareable links

Published as private Claude artifacts (share them from the page's share menu):

- app: https://claude.ai/code/artifact/63c03aa1-2f04-44e1-a885-5dd93c586b90
- test tags: https://claude.ai/code/artifact/a11063ee-ebce-41fc-b0e8-4a0f1193f4d2

Those pages block external requests, so the QR and scanner libraries are inlined into a
build. After editing `index.html` or `tags.html`:

```bash
python build_artifact.py
```

then re-publish `build/app.html` and `build/tags.html` to the same URLs.

## Notes

- The two CDN scripts (QR generator, ZXing) need internet on first load. Offline, the QR
  falls back to plain text and scanning falls back to the type-a-code box.
- `cert.pem` / `key.pem` are generated on first https run and reused. If your LAN IP
  changes, `serve.py` regenerates them automatically.
- Wipe all local state from settings → *Wipe bag + vault*.

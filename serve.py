#!/usr/bin/env python3
"""
Serve this folder over HTTPS so the phone camera actually works.

    python serve.py            # https on 8443, cert covers this machine's LAN IP
    python serve.py --port 9000
    python serve.py --http     # plain http (camera works on localhost only)

Browsers only hand out the camera on a "secure context": https:// or
http://localhost. A self-signed cert is untrusted, so the phone shows a
warning once -- tap Advanced -> Proceed. After that the camera works.
"""

import argparse
import http.server
import ipaddress
import os
import shutil
import socket
import ssl
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.join(HERE, "cert.pem")
KEY = os.path.join(HERE, "key.pem")


def lan_ip():
    """Best-effort local address other devices on the wifi can reach."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def cert_covers(ip):
    """True if an existing cert already lists this IP, so we can reuse it."""
    openssl = shutil.which("openssl")
    if not openssl:
        return True  # no way to check; assume it is fine
    done = subprocess.run([openssl, "x509", "-in", CERT, "-noout", "-text"],
                          capture_output=True, text=True)
    return done.returncode == 0 and ("IP Address:" + ip) in done.stdout


def make_cert(ip):
    openssl = shutil.which("openssl")
    if not openssl:
        return False
    san = "subjectAltName=DNS:localhost,IP:127.0.0.1"
    try:
        ipaddress.ip_address(ip)
        if ip != "127.0.0.1":
            san += ",IP:" + ip
    except ValueError:
        pass
    cmd = [
        openssl, "req", "-x509", "-newkey", "rsa:2048", "-nodes",
        "-keyout", KEY, "-out", CERT, "-days", "365",
        "-subj", "/CN=bonkers-dev",
        "-addext", san,
    ]
    print("generating a self-signed certificate for " + ip + " ...")
    done = subprocess.run(cmd, capture_output=True, text=True)
    if done.returncode != 0:
        print(done.stderr.strip()[:800])
        return False
    return True


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def end_headers(self):
        # never cache while iterating on the app
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stdout.write("  %s\n" % (fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--http", action="store_true", help="plain http, no cert")
    args = ap.parse_args()

    ip = lan_ip()
    port = args.port or (8000 if args.http else 8443)
    scheme = "http" if args.http else "https"

    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler)

    if not args.http:
        have = os.path.exists(CERT) and os.path.exists(KEY)
        if have and not cert_covers(ip):
            print("the existing cert does not cover %s -- regenerating" % ip)
            have = False
        if not have:
            if not make_cert(ip):
                print("\nopenssl not available -- falling back to plain http.")
                print("The camera will then only work at http://localhost:%d\n" % port)
                args.http = True
                scheme = "http"
        if not args.http:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(CERT, KEY)
            httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)

    print("")
    print("  BONKERS is served from " + HERE)
    print("  this machine :  %s://localhost:%d/" % (scheme, port))
    print("  this phone   :  %s://%s:%d/          <- open this on the phone" % (scheme, ip, port))
    print("  test tags    :  %s://%s:%d/tags.html" % (scheme, ip, port))
    if scheme == "https":
        print("")
        print("  The cert is self-signed, so the phone warns once:")
        print("  Chrome -> Advanced -> Proceed, Safari -> Show details -> visit.")
    print("")
    print("  ctrl+c to stop")
    print("")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()

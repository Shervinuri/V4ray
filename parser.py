import base64, requests, os, re, socket
from urllib.parse import urlparse

SOURCE_FILE = "sources.txt"
OUTPUT_FILE = "configs/CollecSHEN.txt"
REMARK = "☬SHΞN™"

COUNTRY_EMOJIS = {
    "ir": "🇮🇷", "de": "🇩🇪", "fr": "🇫🇷", "us": "🇺🇸", "nl": "🇳🇱", "ru": "🇷🇺", "cn": "🇨🇳",
    "in": "🇮🇳", "sg": "🇸🇬", "tr": "🇹🇷", "jp": "🇯🇵", "ca": "🇨🇦", "gb": "🇬🇧"
}

def decode_base64(text):
    padded = text + "=" * ((4 - len(text) % 4) % 4)
    try:
        return base64.b64decode(padded).decode(errors="ignore")
    except:
        return ""

def extract_vless(text):
    configs = set()
    decoded_whole = decode_base64(text.strip())
    if 'vless://' in decoded_whole:
        text += "\n" + decoded_whole

    for line in text.strip().splitlines():
        line = line.strip()
        if not line or len(line) < 10: continue

        if line.startswith('vless://'):
            configs.add(line.split('#')[0])
            continue

        decoded_line = decode_base64(line)
        if 'vless://' in decoded_line:
            configs.update([l.split('#')[0] for l in decoded_line.splitlines() if l.startswith('vless://')])

    return list(configs)

def get_ip(host):
    try:
        return socket.gethostbyname(host)
    except:
        return None

def get_country_flag(ip):
    try:
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        code = r.text.strip().lower()
        return COUNTRY_EMOJIS.get(code, "🏳️")
    except:
        return "🏳️"

def get_network_type(vless_link):
    if "type=grpc" in vless_link:
        return "grpc"
    elif "type=ws" in vless_link:
        return "ws"
    else:
        return "tcp"

def is_alive(host):
    try:
        ip = get_ip(host)
        if not ip: return False
        socket.create_connection((ip, 443), timeout=3)
        return True
    except:
        return False

def generate_remark(host, link):
    ip = get_ip(host)
    flag = get_country_flag(ip) if ip else "🏳️"
    conn = get_network_type(link)
    return f"{REMARK} {flag} {conn}"

def refine_configs(configs):
    refined = []
    for c in configs:
        try:
            parsed = urlparse(c)
            host = parsed.hostname
            if not host or not is_alive(host): continue
            remark = generate_remark(host, c)
            refined.append(c + "#" + remark)
        except:
            continue
    return refined

def fetch_source(url):
    try:
        r = requests.get(url, timeout=10)
        return r.text if r.status_code == 200 else ""
    except:
        return ""

def main():
    os.makedirs("configs", exist_ok=True)
    urls = []
    try:
        with open(SOURCE_FILE, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"Error: {SOURCE_FILE} not found. Please create it and add source URLs.")
        return

    all_configs = []
    for url in urls:
        print(f"🔗 {url}")
        text = fetch_source(url)
        all_configs.extend(extract_vless(text))

    all_configs = list(dict.fromkeys(all_configs))
    print(f"\n🧪 Testing {len(all_configs)} VLESS configs...\n")
    refined = refine_configs(all_configs)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(
            "# درود بر یاران جان\n"
            "# شروین ۱۰ دقیقه دیگه مجدد این لیست رو آپدیت میکنه\n"
            "# پس اگر کانفیگ خوبی پیدا کردی منتقل کن یجا دیگه چون ممکنه که این بره یکی بهتر بیاد جاش 😁\n\n"
        )
        for c in refined:
            f.write(c + "\n")

    print(f"\n✅ Saved {len(refined)} refined configs to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

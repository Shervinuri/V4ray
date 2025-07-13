import base64, requests, os, re

SOURCE_FILE = "sources.txt"
OUTPUT_FILE = "configs/CollecSHEN.txt"
REMARK = "☬SHΞN™"

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode() in s
    except:
        return False

def decode_base64_block(text):
    try:
        padded = text + "=" * ((4 - len(text) % 4) % 4)
        return base64.b64decode(padded).decode(errors='ignore')
    except:
        return ""

def extract_configs(text):
    configs = set()
    # مرحله ۱: اگر کل فایل base64 بود
    decoded_whole = decode_base64_block(text.strip())
    if decoded_whole and any(proto in decoded_whole for proto in ['vmess://', 'vless://', 'ss://']):
        text += "\n" + decoded_whole

    # مرحله ۲: خط‌به‌خط بررسی
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or len(line) < 10:
            continue

        # اگر خودش base64 بود، دیکد کن
        decoded_line = decode_base64_block(line)
        if any(proto in decoded_line for proto in ['vmess://', 'vless://', 'ss://']):
            text += "\n" + decoded_line
            continue

        # اگه خودش کانفیگ بود
        if re.match(r"^(vmess|vless|ss)://", line):
            config = line.split('#')[0] + '#' + REMARK
            configs.add(config)

    return list(configs)

def fetch_url(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.text
    except:
        pass
    return ""

def main():
    os.makedirs("configs", exist_ok=True)
    final_configs = []

    with open(SOURCE_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    for url in urls:
        print(f"🔗 Fetching from: {url}")
        raw = fetch_url(url)
        extracted = extract_configs(raw)
        print(f"✅ Found {len(extracted)} configs")
        final_configs.extend(extracted)

    final_configs = list(dict.fromkeys(final_configs))
    with open(OUTPUT_FILE, 'w') as f:
        for c in final_configs:
            f.write(c + '\n')

    print(f"\n🔥 Saved {len(final_configs)} configs to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

import base64
import requests
import os

SOURCE_FILE = "sources.txt"
OUTPUT_FILE = "configs/CollecSHEN.txt"
REMARK = "☬SHΞN™"

def extract_configs_from_text(text):
    configs = []
    lines = text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            decoded = base64.b64decode(line + '===').decode()
            if 'vmess://' in decoded or 'vless://' in decoded or 'ss://' in decoded:
                lines += decoded.strip().splitlines()
                continue
        except:
            pass
        if line.startswith(("vmess://", "vless://", "ss://")):
            configs.append(remodify_config(line))
    return configs

def remodify_config(config):
    if '#' in config:
        config = config.split('#')[0]
    return config + '#' + REMARK

def fetch_source(url):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.text
    except:
        pass
    return ""

def main():
    os.makedirs("configs", exist_ok=True)
    all_configs = []
    with open(SOURCE_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    for url in urls:
        print(f"Fetching: {url}")
        text = fetch_source(url)
        configs = extract_configs_from_text(text)
        all_configs.extend(configs)

    all_configs = list(dict.fromkeys(all_configs))

    with open(OUTPUT_FILE, 'w') as f:
        for c in all_configs:
            f.write(c + '\n')

    print(f"Saved {len(all_configs)} configs to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

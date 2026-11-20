import re
import subprocess
import sys
import tempfile
import os

def verify_file(filepath):
    print(f"--- Verifying {filepath} ---")
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Check ID references
    js_ids = re.findall(r'getElementById\(["\']([^"\']+)["\']\)', html)
    html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', html))
    
    missing = []
    for jid in js_ids:
        if jid not in html_ids:
            missing.append(jid)
    
    if missing:
        print(f"❌ Missing HTML IDs for JS getElementById: {set(missing)}")
    else:
        print(f"✅ All {len(js_ids)} getElementById references match existing HTML elements.")

    # 2. Extract scripts and test syntax with node via temp file
    scripts = re.findall(r'<script(?:\s+[^>]*)?>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(scripts)} <script> tags.")
    for idx, sc in enumerate(scripts):
        if not sc.strip():
            continue
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tmp:
            tmp.write(sc)
            tmp_path = tmp.name
        try:
            res = subprocess.run(['node', '--check', tmp_path], capture_output=True, text=True)
            if res.returncode != 0:
                print(f"❌ SyntaxError in script #{idx+1}: {res.stderr[:300]}")
                return False
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    print(f"✅ {filepath} verified successfully.")
    return len(missing) == 0

if __name__ == '__main__':
    ok1 = verify_file('index.html')
    ok2 = verify_file('dh.html')
    if not (ok1 and ok2):
        sys.exit(1)

import sys
import urllib.request

URL = "http://127.0.0.1:8000/health"
TIMEOUT = 3.0

try:
    with urllib.request.urlopen(URL, timeout=TIMEOUT) as resp:
        if resp.status == 200:
            sys.exit(0)
except Exception:
    pass

sys.exit(1)

# facecheck_search.py  (strict token required)
"""
Called by run_automations.py:
    python facecheck_search.py <image_path>

Output lines (captured by UI):
    FACECHECK_ERROR <msg>
    FACECHECK_PROGRESS <percent>
    FACECHECK_MATCH <score> <url>
    FACECHECK_DONE
"""

import sys, time, json, requests, os

SITE   = "https://facecheck.id"
CONFIG = "config.json"

def load_settings():
    if not os.path.exists(CONFIG):
        print("FACECHECK_ERROR API_TOKEN_MISSING (config.json not found)")
        sys.exit(1)

    try:
        with open(CONFIG, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError:
        print("FACECHECK_ERROR API_TOKEN_MISSING (config.json invalid)")
        sys.exit(1)

    face_cfg = cfg.get("providers", {}).get("facecheck", {})

    token   = face_cfg.get("api_token", "").strip()
    testing = bool(face_cfg.get("testing_mode", True))

    if not token:
        print("FACECHECK_ERROR API_TOKEN_MISSING")
        sys.exit(1)

    return token, testing

def main():
    if len(sys.argv) < 2:
        print("FACECHECK_ERROR need image path")
        return

    image_path = sys.argv[1]
    api_token, testing_mode = load_settings()
    if "--test" in sys.argv:  # CLI flag overrides config
        testing_mode = True

    if testing_mode:
        print("TESTING MODE ACTIVATED")

    headers = {"accept": "application/json", "Authorization": api_token}
    files   = {"images": open(image_path, "rb"), "id_search": None}

    # 1) upload
    resp = requests.post(f"{SITE}/api/upload_pic", headers=headers, files=files).json()
    if resp.get("error"):
        print("FACECHECK_ERROR", resp["error"])
        return

    search_id = resp["id_search"]
    payload = {"id_search": search_id, "with_progress": True,
               "status_only": False, "demo": testing_mode}

    # 2) poll
    while True:
        r = requests.post(f"{SITE}/api/search", headers=headers, json=payload).json()
        if r.get("error"):
            print("FACECHECK_ERROR", r["error"])
            return
        if r["output"]:
            break
        print("FACECHECK_PROGRESS", r["progress"])
        time.sleep(1)

    # 3) matches
    for itm in r["output"]["items"]:
        print("FACECHECK_MATCH", itm["score"], itm["url"])

    print("FACECHECK_DONE")

if __name__ == "__main__":
    main()

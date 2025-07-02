#!/usr/bin/env python
import sys, subprocess, os, datetime, time, json

# ---------- paths / constants ----------
CONFIG_FILE = "config.json"
SRC_DIR     = "Source_Images"
IMG_PATH    = os.path.join(SRC_DIR, "Webcam_Capture.jpg")

TAKE_PIC    = "takePicture.py"
PIMEYES     = "main.py"
FACECHECK   = "facecheck_search.py"

LOG_DIR     = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

TS        = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE  = os.path.join(LOG_DIR, f"log_{TS}.txt")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------- helpers ----------
def load_cfg() -> dict:
    default = {
        "webcam_index": 0,
        "providers": {
            "pimeyes":   { "enabled": True },
            "facecheck": { "enabled": True, "testing_mode": True }
        }
    }
    if not os.path.exists(CONFIG_FILE):
        return default
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError:
        print("Config corrupted, using defaults.")
        return default

    # merge shallow
    cfg.setdefault("webcam_index", default["webcam_index"])
    cfg.setdefault("providers",   default["providers"])
    for k, v in default["providers"].items():
        cfg["providers"].setdefault(k, v)
    return cfg


def run(cmd, log_f):
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", bufsize=1
    )
    for line in proc.stdout:
        print(line, end="")
        log_f.write(line)
    proc.wait()
    return proc.returncode


# ---------- main pipeline ----------
def main():
    cfg       = load_cfg()
    prov      = cfg["providers"]
    cam_idx   = cfg["webcam_index"]

    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write(f"==== run {TS} ====\n")

        # STEP 1 – capture
        log.write("[1] takePicture.py …\n")
        if run([sys.executable, TAKE_PIC, "-i", str(cam_idx)], log) != 0 \
           or not os.path.exists(IMG_PATH):
            log.write("ERROR: capture failed.\n"); return

        print("SNAP_COMPLETE", flush=True)
        log.write("SNAP_COMPLETE\n"); log.flush()
        time.sleep(2)          # give UI time to load preview

        step = 2

        # STEP 2 – PimEyes
        if prov["pimeyes"]["enabled"]:
            log.write(f"[{step}] {PIMEYES} …\n")
            run([sys.executable, PIMEYES, IMG_PATH], log)
            step += 1
        else:
            log.write("PimEyes disabled in config.\n")

        # STEP 3 – FaceCheck
        if prov["facecheck"]["enabled"]:
            cmd = [sys.executable, FACECHECK, IMG_PATH]
            if prov["facecheck"].get("testing_mode", True):
                cmd.append("--test")
            log.write(f"[{step}] {FACECHECK} …\n")
            run(cmd, log)
        else:
            log.write("FaceCheck disabled in config.\n")

        log.write("==== finished ====\n")

    print(f"\nLog saved to {LOG_FILE}")


if __name__ == "__main__":
    main()

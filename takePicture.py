# takePicture.py  (non-interactive)
import cv2, os, time, argparse, sys

SAVE_DIR  = "Source_Images"
SAVE_FILE = "Webcam_Capture.jpg"
os.makedirs(SAVE_DIR, exist_ok=True)

def capture(index: int) -> str | None:
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"ERROR: cannot open webcam {index}")
        return None
    print(f"Capturing from webcam {index} ...")
    time.sleep(1)                                 # warm-up
    ok, frame = cap.read()
    cap.release()
    if not ok:
        print("ERROR: failed to grab frame")
        return None
    path = os.path.join(SAVE_DIR, SAVE_FILE)
    cv2.imwrite(path, frame)
    print(f"Saved {path}")
    return path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--index", type=int, default=0,
                        help="webcam index (default 0)")
    args = parser.parse_args()
    result = capture(args.index)
    sys.exit(0 if result else 1)

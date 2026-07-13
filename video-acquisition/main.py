import cv2
import time

RTSP_URL = "rtsp://localhost:8554/cam2"

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    print("Failed to open stream:", RTSP_URL)
    exit()

print("Stream opened successfully. Reading frames... (Ctrl+C to stop)")

frame_count = 0
total_frames = 0
start_time = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame not received, retrying...")
            time.sleep(0.5)
            continue

        frame_count += 1
        total_frames += 1
        elapsed = time.time() - start_time

        if elapsed >= 1.0:
            fps = frame_count / elapsed
            h, w = frame.shape[:2]
            print(f"FPS: {fps:.2f} | Resolution: {w}x{h} | Total frames: {total_frames}")
            frame_count = 0
            start_time = time.time()

except KeyboardInterrupt:
    print("Stopped by user.")

cap.release()
print("Stream closed.")
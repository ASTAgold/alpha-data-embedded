import cv2
import threading
from typing import Optional, Tuple, List


class RTSPCameraStream:
    """
    A class to handle one RTSP stream using OpenCV and threading.
    """

    def __init__(self, url: str):
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        self.is_running = False
        self.lock = threading.Lock()
        self.frame: Optional[Tuple[bool, any]] = None
        self.thread = None

    def start(self) -> None:
        self.is_running = True
        self.thread = threading.Thread(target=self._update_frame, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.is_running = False
        if self.thread is not None:
            self.thread.join(timeout=1)
        if self.cap.isOpened():
            self.cap.release()

    def _update_frame(self) -> None:
        while self.is_running:
            ret, frame = self.cap.read()
            with self.lock:
                self.frame = (ret, frame)

    def read(self) -> Tuple[bool, Optional[any]]:
        with self.lock:
            if self.frame is not None:
                ret, frame = self.frame
                if ret and frame is not None:
                    return ret, frame.copy()
                return ret, frame
            return False, None


def resize_to_same_height(frames, target_height=360):
    resized = []
    for frame in frames:
        h, w = frame.shape[:2]
        new_width = int(w * (target_height / h))
        resized_frame = cv2.resize(frame, (new_width, target_height))
        resized.append(resized_frame)
    return resized


def main():
    stream_urls: List[str] = [
        "rtsp://192.168.8.95:8554/cam1",
        "rtsp://192.168.8.95:8554/cam2",
        # "rtsp://localhost:8554/cam3",
        # "rtsp://localhost:8554/cam4",
        # "rtsp://localhost:8554/cam5",
        # add more here
    ]

    streams = [RTSPCameraStream(url) for url in stream_urls]

    for stream in streams:
        stream.start()

    try:
        while True:
            frames = []

            for i, stream in enumerate(streams):
                ret, frame = stream.read()

                if ret and frame is not None:
                    cv2.putText(
                        frame,
                        f"cam {i+1}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )
                    frames.append(frame)

            if frames:
                frames = resize_to_same_height(frames, target_height=360)
                combined = cv2.hconcat(frames)
                cv2.imshow("RTSP Streams", combined)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break

    finally:
        for stream in streams:
            stream.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
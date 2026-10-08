"""Compare local adapters on identical image inputs, without camera/app actions."""
import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from person_detector import create_detector


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", type=Path, nargs="+")
    parser.add_argument("--model", type=Path, default=Path("yolo26s.pt"))
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("--iterations must be positive")
    frames = [cv2.imread(str(path)) for path in args.images]
    if any(frame is None for frame in frames):
        parser.error("Every input must be a readable local image")
    report = {"platform": platform.platform(), "model": str(args.model), "imgsz": args.imgsz,
              "scope": "warm adapter wall time incl. preprocessing and NMS; no camera, tracking, UI or app hide",
              "preprocessing": "PyTorch preserves original rectangular padding; Core ML uses fixed square padding",
              "iterations_per_image": args.iterations, "warmups_per_image": 3, "backends": {}}
    for backend in ("pytorch", "coreml"):
        started = time.perf_counter()
        detector = create_detector(args.model, backend=backend, imgsz=args.imgsz, model_dirs=(Path(".models"),))
        load_ms = (time.perf_counter() - started) * 1000
        if detector.notice:
            raise RuntimeError(detector.notice)
        measurements = []
        for path, frame in zip(args.images, frames):
            for _ in range(3):
                detector.detect(frame, 0.30, args.imgsz)
            samples = []
            for _ in range(args.iterations):
                start = time.perf_counter()
                detections = detector.detect(frame, 0.30, args.imgsz)
                samples.append((time.perf_counter() - start) * 1000)
            if detector.notice:
                raise RuntimeError(detector.notice)
            samples.sort()
            measurements.append({"image": str(path), "p50_ms": statistics.median(samples),
                                 "p95_ms": samples[min(len(samples) - 1, int(len(samples) * .95))],
                                 "detections": detections})
        report["backends"][backend] = {"actual_backend": detector.description,
                                         "load_ms": load_ms, "images": measurements}
    result = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result + "\n", encoding="utf-8")
    print(result)


if __name__ == "__main__":
    main()

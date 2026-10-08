"""Local person detection with a Core ML adapter and a PyTorch fallback.

Both adapters return original-frame xyxy boxes. Core ML packages must come
from tools/export_coreml.py: fixed square input, raw YOLO COCO detection
head, RGB image input. Unsupported exports fail visibly instead of guessing.
"""
import hashlib
import json
import platform
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def input_size(imgsz):
    return int(np.ceil(imgsz / 32) * 32)


def model_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def package_name(model_path, imgsz):
    return f"{Path(model_path).stem}-{input_size(imgsz)}.mlpackage"


def letterbox(frame, size):
    height, width = frame.shape[:2]
    gain = min(size / height, size / width)
    resized = cv2.resize(frame, (round(width * gain), round(height * gain)))
    dw, dh = (size - resized.shape[1]) / 2, (size - resized.shape[0]) / 2
    left, top = round(dw - 0.1), round(dh - 0.1)
    padded = cv2.copyMakeBorder(resized, top, round(dh + 0.1), left,
                               round(dw + 0.1), cv2.BORDER_CONSTANT, value=(114, 114, 114))
    return Image.fromarray(cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)), gain, (left, top)


def decode_person_boxes(raw, gain, padding, frame_shape, confidence, iou_threshold=0.7):
    predictions = np.asarray(raw)
    if predictions.ndim != 3 or predictions.shape[0] != 1 or predictions.shape[1] != 84:
        raise ValueError(f"Unsupported Core ML output shape: {predictions.shape}; expected (1, 84, N)")
    predictions = predictions[0].T
    scores = predictions[:, 4:]
    # Match Ultralytics' single-label prediction, then filter to COCO person.
    valid = (scores.argmax(axis=1) == 0) & (scores[:, 0] > confidence)
    predictions = predictions[valid]
    if not len(predictions):
        return []
    centers, sizes = predictions[:, :2], predictions[:, 2:4]
    boxes = np.column_stack((centers - sizes / 2, centers + sizes / 2)).astype(np.float32)
    scores = predictions[:, 4]
    order = np.argsort(-scores, kind="stable")[:30000]
    kept = []
    # NMS happens in model coordinates, before clipping/rescaling, like PyTorch.
    while len(order) and len(kept) < 300:
        index = order[0]
        kept.append(index)
        remaining = order[1:]
        low = np.maximum(boxes[index, :2], boxes[remaining, :2])
        high = np.minimum(boxes[index, 2:], boxes[remaining, 2:])
        intersection = np.maximum(high - low, 0).prod(axis=1)
        area = np.maximum(boxes[index, 2:] - boxes[index, :2], 0).prod()
        other_area = np.maximum(boxes[remaining, 2:] - boxes[remaining, :2], 0).prod(axis=1)
        overlap = intersection / np.maximum(area + other_area - intersection, 1e-7)
        order = remaining[overlap <= iou_threshold]
    boxes[:, [0, 2]] = (boxes[:, [0, 2]] - padding[0]) / gain
    boxes[:, [1, 3]] = (boxes[:, [1, 3]] - padding[1]) / gain
    height, width = frame_shape[:2]
    boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, width)
    boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, height)
    return [{"box": tuple(float(x) for x in boxes[index]), "confidence": float(scores[index])}
            for index in kept]


class _PyTorchDetector:
    def __init__(self, model_path):
        import torch
        from ultralytics import YOLO

        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.model = YOLO(str(model_path), task="detect")
        # Use the same one-to-many COCO head and NMS contract as our native export.
        # YOLO26 otherwise defaults to the different end-to-end detection branch.
        if hasattr(self.model.model, "end2end"):
            self.model.model.end2end = False
        self.description = f"PyTorch / {self.device.upper()}"

    def detect(self, frame, confidence, imgsz):
        result = self.model.predict(source=frame, classes=[0], conf=confidence,
                                    imgsz=input_size(imgsz), rect=True, verbose=False,
                                    device=self.device)[0]
        if result.boxes is None:
            return []
        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()
        return [{"box": tuple(float(x) for x in box), "confidence": float(score)}
                for box, score in zip(boxes, scores)]


class _CoreMLDetector:
    def __init__(self, package, source_model, imgsz):
        import coremltools as ct

        manifest = json.loads(Path(str(package) + ".json").read_text(encoding="utf-8"))
        supported_head = ((manifest.get("schema_version"), manifest.get("head")) in
                          ((1, "yolo11-coco-raw"), (2, "yolo-coco-raw")))
        if (not supported_head
                or manifest.get("imgsz") != input_size(imgsz)
                or manifest.get("source_sha256") != model_digest(source_model)):
            raise ValueError("Core ML export does not match the selected weights, head, or detection size")
        self.size = manifest["imgsz"]
        # Allow CPU + ANE. Actual placement is chosen by Core ML, not guaranteed.
        self.model = ct.models.MLModel(str(package), compute_units=ct.ComputeUnit.CPU_AND_NE)
        spec = self.model.get_spec()
        inputs, outputs = spec.description.input, spec.description.output
        if (len(inputs) != 1 or inputs[0].type.WhichOneof("Type") != "imageType"
                or inputs[0].type.imageType.width != self.size
                or inputs[0].type.imageType.height != self.size
                or inputs[0].type.imageType.colorSpace != ct.proto.FeatureTypes_pb2.ImageFeatureType.RGB
                or len(outputs) != 1):
            raise ValueError("Unsupported Core ML input/output contract")
        if tuple(outputs[0].type.multiArrayType.shape) != (1, 84, 21 * (self.size // 32) ** 2):
            raise ValueError("Unsupported Core ML detection head; expected raw COCO output")
        self.input_name, self.output_name = inputs[0].name, outputs[0].name
        self.description = f"Core ML / CPU + Neural Engine / {self.size}"

    def detect(self, frame, confidence, imgsz):
        if input_size(imgsz) != self.size:
            raise ValueError("Core ML has a fixed input size; prepare an export for this detection size")
        image, gain, padding = letterbox(frame, self.size)
        raw = self.model.predict({self.input_name: image})[self.output_name]
        return decode_person_boxes(raw, gain, padding, frame.shape, confidence)


class PersonDetector:
    """Choose once; if native inference fails, switch to PyTorch for this session."""
    def __init__(self, model_path, backend, imgsz, model_dirs):
        if backend not in ("auto", "coreml", "pytorch"):
            raise ValueError(f"Unknown inference backend: {backend}")
        self.model_path = Path(model_path)
        if not self.model_path.is_file() or self.model_path.suffix != ".pt":
            raise ValueError("Select a local .pt detection model; no weights are downloaded at runtime")
        self.notice = None
        self._active = None
        if backend != "pytorch":
            package = next((Path(directory) / package_name(model_path, imgsz) for directory in model_dirs
                            if (Path(directory) / package_name(model_path, imgsz)).is_dir()), None)
            if package is not None and platform.system() == "Darwin":
                try:
                    self._active = _CoreMLDetector(package, self.model_path, imgsz)
                except Exception as exc:
                    self.notice = f"Core ML unavailable: {exc}. Using PyTorch."
            elif backend == "coreml":
                self.notice = "Core ML export is missing for this detection size. Using PyTorch."
        if self._active is None:
            self._active = _PyTorchDetector(self.model_path)

    @property
    def description(self):
        return self._active.description

    def detect(self, frame, confidence, imgsz):
        try:
            return self._active.detect(frame, confidence, imgsz)
        except Exception as exc:
            if not isinstance(self._active, _CoreMLDetector):
                raise
            self.notice = f"Core ML inference failed: {exc}. Using PyTorch."
            self._active = _PyTorchDetector(self.model_path)
            return self._active.detect(frame, confidence, imgsz)


def create_detector(model_path, backend="auto", imgsz=1280, model_dirs=()):
    return PersonDetector(model_path, backend, imgsz, model_dirs)

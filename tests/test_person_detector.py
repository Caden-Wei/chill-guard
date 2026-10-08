import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np

import person_detector as detector


class DecoderTests(unittest.TestCase):
    def test_nms_class_filter_and_confidence_match_person_only_contract(self):
        raw = np.zeros((1, 84, 4), dtype=np.float32)
        raw[0, :4] = np.array([[100, 102, 400, 500], [200, 202, 200, 200],
                              [50, 50, 50, 50], [100, 100, 100, 100]])
        raw[0, 4] = [.9, .8, .2, .7]
        raw[0, 5, 3] = .95  # A different class wins; person-only must exclude it.
        found = detector.decode_person_boxes(raw, 1, (0, 0), (640, 640, 3), .3)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["box"], (75, 150, 125, 250))

    def test_letterbox_odd_dimensions_and_coordinate_roundtrip(self):
        frame = np.zeros((333, 777, 3), dtype=np.uint8)
        image, gain, padding = detector.letterbox(frame, 640)
        self.assertEqual(image.size, (640, 640))
        original = np.array([100, 50, 500, 300], dtype=np.float32)
        transformed = original * gain + np.array([*padding, *padding])
        raw = np.zeros((1, 84, 1), dtype=np.float32)
        raw[0, :4, 0] = [*(transformed[:2] + transformed[2:]) / 2,
                          *(transformed[2:] - transformed[:2])]
        raw[0, 4, 0] = .9
        result = detector.decode_person_boxes(raw, gain, padding, frame.shape, .3)
        np.testing.assert_allclose(result[0]["box"], original, atol=.001)

    def test_unknown_output_fails_instead_of_silently_counting_zero(self):
        with self.assertRaises(ValueError):
            detector.decode_person_boxes(np.zeros((1, 300, 6)), 1, (0, 0), (640, 640, 3), .3)


class BackendTests(unittest.TestCase):
    def test_missing_native_export_falls_back_and_reports_actual_backend(self):
        fallback = Mock(description="PyTorch / CPU")
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / "yolo11s.pt"
            model.write_bytes(b"weights")
            with patch.object(detector, "_PyTorchDetector", return_value=fallback):
                runner = detector.create_detector(model, "coreml", model_dirs=[directory])
                self.assertEqual(runner.description, "PyTorch / CPU")
                self.assertIn("missing", runner.notice)

    def test_native_runtime_failure_switches_once_and_retries_same_frame(self):
        class BrokenNative:
            description = "Core ML"

            def __init__(self, *args):
                pass

            def detect(self, *args):
                raise RuntimeError("test runtime failure")

        fallback = Mock(description="PyTorch / CPU")
        fallback.detect.return_value = [{"box": (1, 2, 3, 4), "confidence": .9}]
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / "yolo11s.pt"
            model.write_bytes(b"weights")
            (Path(directory) / detector.package_name(model, 1280)).mkdir()
            with patch.object(detector.platform, "system", return_value="Darwin"), \
                    patch.object(detector, "_CoreMLDetector", BrokenNative), \
                    patch.object(detector, "_PyTorchDetector", return_value=fallback) as factory:
                runner = detector.create_detector(model, "auto", model_dirs=[directory])
                frame = np.zeros((100, 100, 3), dtype=np.uint8)
                self.assertEqual(runner.detect(frame, .3, 1280), fallback.detect.return_value)
                runner.detect(frame, .3, 1280)
                factory.assert_called_once()
                self.assertEqual(fallback.detect.call_count, 2)
                self.assertIn("test runtime failure", runner.notice)

    def test_stale_weight_manifest_is_rejected_before_model_loading(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / "yolo11s.pt"
            model.write_bytes(b"new weights")
            package = Path(directory) / "yolo11s-1280.mlpackage"
            Path(str(package) + ".json").write_text(json.dumps({
                "schema_version": 1, "head": "yolo11-coco-raw", "imgsz": 1280,
                "source_sha256": "wrong hash",
            }))
            fake_coreml = Mock()
            with patch.dict("sys.modules", {"coremltools": fake_coreml}):
                with self.assertRaisesRegex(ValueError, "does not match"):
                    detector._CoreMLDetector(package, model, 1280)
                fake_coreml.models.MLModel.assert_not_called()


if __name__ == "__main__":
    unittest.main()

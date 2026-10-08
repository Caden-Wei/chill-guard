"""Exercise the real settings and monitor paths without camera or app automation."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import numpy as np

import chill_guard_app as app


class SettingsTests(unittest.TestCase):
    def test_saved_user_choices_survive_restart(self):
        settings = app.GuardSettings(
            model_name="yolo11n.pt", trigger_frame_threshold=4,
            far_target_boost_enabled=True, far_target_confidence=0.25,
            detect_imgsz=640, frame_scale=0.5, confidence_threshold=0.5,
        )
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(app, "SETTINGS_PATH", Path(directory) / "settings.json"):
                app.save_settings(settings)
                restored = app.load_settings()
        self.assertEqual(app.settings_to_dict(restored), app.settings_to_dict(settings))

    def test_unversioned_settings_preserve_explicit_choices(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(json.dumps({"trigger_frame_threshold": 5, "model_name": "yolo11n.pt"}))
            with patch.object(app, "SETTINGS_PATH", path):
                settings = app.load_settings()
        self.assertEqual(settings.trigger_frame_threshold, 5)
        self.assertEqual(settings.model_name, "yolo11n.pt")

    def test_native_backend_choice_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(app, "SETTINGS_PATH", Path(directory) / "settings.json"):
                app.save_settings(app.GuardSettings(inference_backend="coreml"))
                self.assertEqual(app.load_settings().inference_backend, "coreml")

    def test_malformed_field_types_use_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(json.dumps({"blacklist_apps": "Safari", "model_name": None,
                                        "inference_backend": "unknown"}))
            with patch.object(app, "SETTINGS_PATH", path):
                settings = app.load_settings()
        self.assertEqual(settings.blacklist_apps, app.DEFAULT_BLACKLIST)
        self.assertEqual(settings.model_name, "yolo26s.pt")
        self.assertEqual(settings.inference_backend, "coreml")


class MonitorTests(unittest.TestCase):
    def run_frames(self, extra_boxes, threshold=1, allowed=1, muted=False):
        settings = app.GuardSettings(preview_enabled=False, alert_sound_enabled=False,
                                     trigger_frame_threshold=threshold, max_allowed_people=allowed)
        runtime = SimpleNamespace(
            get_settings=lambda: settings, stop_event=threading.Event(),
            frame_counter=0, cached_far_detections=[], running=True,
            queue_alert=Mock(return_value=True), is_muted_until_release=lambda: muted,
            set_latest_preview=Mock(), set_live_people_count=Mock(),
        )
        frame = np.zeros((1000, 1000, 3), dtype=np.uint8)
        index = [0]

        def read():
            index[0] += 1
            if index[0] == len(extra_boxes):
                runtime.stop_event.set()
            return True, frame

        def detections(*args, **kwargs):
            return [{"box": (350, 200, 650, 700), "confidence": 0.95}] + [
                {"box": box, "confidence": 0.8} for box in extra_boxes[index[0] - 1]
            ]

        camera = Mock()
        camera.read.side_effect = read
        with patch.object(app.cv2, "VideoCapture", return_value=camera), \
                patch.object(app, "create_detector", return_value=SimpleNamespace(
                    detect=detections, description="Test detector", notice=None)):
            app.monitor_loop(runtime, Mock())
        camera.release.assert_called_once()
        return runtime

    def test_tiny_target_excluded_by_rule_does_not_hide_apps(self):
        self.assertEqual(self.run_frames([[(20, 20, 25, 25)]]).queue_alert.call_count, 0)

    def test_buffer_target_excluded_by_rule_does_not_hide_apps(self):
        self.assertEqual(self.run_frames([[(270, 450, 340, 650)]]).queue_alert.call_count, 0)

    def test_eligible_extra_person_hides_apps(self):
        self.assertEqual(self.run_frames([[(20, 20, 100, 220)]]).queue_alert.call_count, 1)

    def test_single_frame_extra_person_obeys_saved_threshold(self):
        self.assertEqual(self.run_frames([[(20, 20, 100, 220)], []], threshold=3).queue_alert.call_count, 0)

    def test_allowed_people_limit_is_respected(self):
        self.assertEqual(self.run_frames([[(20, 20, 100, 220)]], allowed=2).queue_alert.call_count, 0)

    def test_hold_to_mute_suppresses_app_hide(self):
        self.assertEqual(self.run_frames([[(20, 20, 100, 220)]], muted=True).queue_alert.call_count, 0)

    def test_low_confidence_merged_duplicate_cannot_replace_main_user(self):
        runtime = self.run_frames([[(300, 200, 800, 700), (700, 200, 950, 700)]])
        self.assertEqual(runtime.queue_alert.call_count, 1)


class StatusTests(unittest.TestCase):
    def test_camera_and_settings_messages_keep_running_indicator(self):
        view = app.ChillGuardApp.__new__(app.ChillGuardApp)
        view.runtime = SimpleNamespace(get_live_people_count=lambda: 1, running=True,
                                       is_muted_until_release=lambda: False)
        view.entries = {}
        view.preview_chip_people_var = Mock()
        view.preview_chip_state_var = Mock()
        view.status_pill_var = Mock()
        view.update_status_layout = Mock()
        for message in ("Camera connected", "Settings applied", "Alert sound disabled"):
            view.update_runtime_chips(message)
            view.preview_chip_state_var.set.assert_called_with("Monitoring")
        view.update_runtime_chips("Alert failed: permission denied")
        view.preview_chip_state_var.set.assert_called_with("Error")
        view.update_runtime_chips("Monitoring stopped: Cannot open camera")
        view.preview_chip_state_var.set.assert_called_with("Error")


if __name__ == "__main__":
    unittest.main()

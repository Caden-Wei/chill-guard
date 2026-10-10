"""Exercise real Tk controls without camera, hotkey registration or app hiding."""
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import chill_guard_app as app
from chill_guard_i18n import TEXT


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.patches = [patch.object(app, "SETTINGS_PATH", Path(self.directory.name) / "settings.json")]
        self.patches += [patch.object(app, "append_log")]
        self.patches += [patch.object(app.ChillGuardApp, name) for name in
                         ("setup_status_bar", "start_hotkey_listener", "refresh_hotkey_status", "refresh_preview")]
        for item in self.patches:
            item.start()
        self.settings = app.GuardSettings(
            blacklist_apps=["Safari", "iPhone Mirroring", "WeChat", "Telegram", "QQ Music", "Photos"],
            start_stop_hotkey="<cmd>+<ctrl>+<alt>+<keycode:27>", mute_hold_hotkey="<keycode:99>",
            preview_enabled=False, launch_at_login=True, camera_width=1280, camera_height=720,
        )
        app.save_settings(self.settings)
        self.root = tk.Tk()
        self.view = app.ChillGuardApp(self.root)
        self.root.update()

    def tearDown(self):
        self.view.ui_task_polling = False
        self.root.destroy()
        for item in reversed(self.patches):
            item.stop()
        self.directory.cleanup()

    def test_language_switch_preserves_pending_edits_and_saved_keycodes(self):
        entry = self.view.entries["trigger_frame_threshold"]
        entry.delete(0, "end")
        entry.insert(0, "4")
        self.view.ui.language_var.set("English")
        self.view.ui.change_language()
        self.assertEqual(entry.get(), "4")
        self.assertEqual(app.load_settings().language, "en")
        self.assertEqual(app.load_settings().trigger_frame_threshold, 1)
        self.assertTrue(self.view.apply_settings())
        restored = app.load_settings()
        self.assertEqual(restored.trigger_frame_threshold, 4)
        for key in ("blacklist_apps", "start_stop_hotkey", "mute_hold_hotkey", "launch_at_login",
                    "preview_enabled", "camera_width", "camera_height"):
            self.assertEqual(getattr(restored, key), getattr(self.settings, key), key)
        self.assertEqual(self.view.ui.primary_button.cget("text"), "Start protection")
        self.view.ui.language_var.set("中文")
        self.view.ui.change_language()
        self.assertEqual(self.view.ui.primary_button.cget("text"), "开始保护")
        self.assertEqual(self.view.get_blacklist_items(), self.settings.blacklist_apps)
        self.assertEqual(self.view.ui.menu.entrycget(0, "label"), "文件")

    def test_restore_detection_keeps_protected_user_choices(self):
        self.view.reset_defaults()
        restored = app.load_settings()
        for key in ("blacklist_apps", "start_stop_hotkey", "mute_hold_hotkey", "launch_at_login",
                    "preview_enabled", "alert_sound_enabled", "language"):
            self.assertEqual(getattr(restored, key), getattr(self.settings, key), key)

    def test_every_visible_static_control_has_a_chinese_translation(self):
        for _, key in self.view.ui.bindings:
            self.assertIn(key, TEXT)

    def test_advanced_controls_and_language_stay_reachable_at_minimum_size(self):
        self.root.geometry("1000x690")
        self.view.switch_settings_panel("parameters")
        self.view.show_monitor_advanced_view()
        self.root.update()
        self.assertTrue(self.view.ui.language_buttons["en"].winfo_ismapped())
        self.assertEqual(self.view.parameters_toggle_button.cget("text"), "返回基础设置")
        self.assertGreater(self.view.entries["far_target_confidence"].winfo_width(), 100)
        self.view.show_monitor_basic_view()
        self.root.update()
        self.assertEqual(self.view.parameters_toggle_button.cget("text"), "高级设置")

    def test_model_loading_has_starting_state_and_preview_returns_to_empty(self):
        import numpy as np
        self.view.runtime.running = True
        self.view.set_status("Loading model...")
        self.assertEqual(self.view.status_pill_var.get(), "Starting")
        self.assertEqual(self.view.ui.state_note.get(), "正在准备摄像头")
        self.assertEqual(self.view.ui.engine_title.get(), "已配置引擎")
        self.view.ui.update_preview(np.zeros((360, 640, 3), dtype=np.uint8))
        self.root.update()
        self.assertFalse(self.view.ui.empty_preview.winfo_ismapped())
        self.view.ui.update_preview(None)
        self.root.update()
        self.assertTrue(self.view.ui.empty_preview.winfo_ismapped())
        self.assertFalse(self.view.preview_label.winfo_ismapped())
        self.view.ui.update_preview(np.ones((360, 640, 3), dtype=np.uint8))
        self.root.update()
        self.assertTrue(self.view.preview_label.winfo_ismapped())
        self.assertFalse(self.view.ui.empty_preview.winfo_ismapped())
        self.view.runtime.running = False
        self.view.set_status("Monitoring stopped")
        self.assertEqual(self.view.status_pill_var.get(), "Standby")

    def test_throttled_monitor_frames_keep_live_preview_without_loading_overlay(self):
        import numpy as np
        runtime = self.view.runtime
        runtime.running = True
        runtime.set_preview_enabled(True)
        self.view.preview_var.set(True)
        frame = np.full((360, 640, 3), 120, dtype=np.uint8)
        observations = []
        reads = 0

        def read():
            nonlocal reads
            if reads:
                latest = runtime.get_latest_preview()
                self.view.ui.update_preview(latest)
                self.root.update()
                observations.append((latest is not None, bool(self.view.ui.empty_preview.winfo_ismapped())))
            reads += 1
            if reads == 6:
                runtime.stop_event.set()
            return True, frame

        camera = Mock()
        camera.read.side_effect = read
        detector = SimpleNamespace(detect=lambda *_: [], description="Test detector", notice=None)
        with patch.object(app.cv2, "VideoCapture", return_value=camera), \
                patch.object(app, "create_detector", return_value=detector), \
                patch.object(runtime, "can_publish_preview", side_effect=[True, False, False, True, False, False]):
            app.monitor_loop(runtime, self.view.set_status)
        self.assertEqual(observations, [(True, False)] * 5)
        self.view.ui.update_preview(runtime.get_latest_preview())
        self.root.update()
        self.assertTrue(self.view.ui.empty_preview.winfo_ismapped())
        self.assertFalse(self.view.preview_label.winfo_ismapped())
        camera.release.assert_called_once()

    def test_drawn_button_mouse_and_keyboard_activation_use_same_action(self):
        self.view.switch_settings_panel("parameters")
        self.root.update()
        button = self.view.parameters_toggle_button
        button._canvas.event_generate("<Button-1>", x=25, y=15)
        self.root.update()
        self.assertEqual(self.view.monitor_mode_var.get(), "advanced")
        button._canvas.focus_force()
        button._canvas.event_generate("<KeyPress-space>")
        self.root.update()
        self.assertEqual(self.view.monitor_mode_var.get(), "basic")

    def test_all_six_overview_rows_fit_at_minimum_size(self):
        self.root.geometry("1000x690")
        self.view.switch_settings_panel("overview")
        self.root.update()
        rows = self.view.ui.overview_app_rows.winfo_children()
        self.assertEqual(len(rows), 6)
        last = rows[-1]
        self.assertLessEqual(last.winfo_rooty() + last.winfo_height(),
                             self.view.ui.overview_apps.winfo_rooty() + self.view.ui.overview_apps.winfo_height() - 5)


if __name__ == "__main__":
    unittest.main()

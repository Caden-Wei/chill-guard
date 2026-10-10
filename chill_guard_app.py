import ctypes
from ctypes.util import find_library
import json
import math
import os
import queue
import re
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from AppKit import (
    NSApplication,
    NSBeep,
    NSMenu,
    NSMenuItem,
    NSObject,
    NSEvent,
    NSEventMaskFlagsChanged,
    NSEventMaskKeyDown,
    NSEventMaskKeyUp,
    NSEventTypeFlagsChanged,
    NSEventTypeKeyDown,
    NSEventTypeKeyUp,
)
from ApplicationServices import AXIsProcessTrusted, AXIsProcessTrustedWithOptions, kAXTrustedCheckOptionPrompt
from PIL import Image, ImageOps, ImageTk
from person_detector import create_detector
from chill_guard_ui import build_form as build_workspace, setup_theme as setup_workspace_theme
from chill_guard_i18n import Language
import objc
import Quartz


def four_char_code(text):
    return int.from_bytes(text.encode("latin-1"), "big")


class CarbonEventTypeSpec(ctypes.Structure):
    _fields_ = [
        ("eventClass", ctypes.c_uint32),
        ("eventKind", ctypes.c_uint32),
    ]


class CarbonEventHotKeyID(ctypes.Structure):
    _fields_ = [
        ("signature", ctypes.c_uint32),
        ("id", ctypes.c_uint32),
    ]


CARBON_EVENT_HANDLER_CALLBACK = ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
CARBON = None
CARBON_AVAILABLE = False
CARBON_KEYBOARD_EVENT_CLASS = four_char_code("keyb")
CARBON_HOTKEY_PRESSED = 5
CARBON_HOTKEY_RELEASED = 6
CARBON_EVENT_PARAM_DIRECT_OBJECT = four_char_code("----")
CARBON_TYPE_EVENT_HOTKEY_ID = four_char_code("hkid")
CARBON_HOTKEY_SIGNATURE = four_char_code("CGHK")
CARBON_CMD_KEY = 1 << 8
CARBON_SHIFT_KEY = 1 << 9
CARBON_OPTION_KEY = 1 << 11
CARBON_CONTROL_KEY = 1 << 12

try:
    carbon_library_path = find_library("Carbon") or "/System/Library/Frameworks/Carbon.framework/Carbon"
    CARBON = ctypes.CDLL(carbon_library_path)
    CARBON.GetApplicationEventTarget.restype = ctypes.c_void_p
    CARBON.GetEventClass.argtypes = [ctypes.c_void_p]
    CARBON.GetEventClass.restype = ctypes.c_uint32
    CARBON.GetEventKind.argtypes = [ctypes.c_void_p]
    CARBON.GetEventKind.restype = ctypes.c_uint32
    CARBON.InstallEventHandler.argtypes = [
        ctypes.c_void_p,
        CARBON_EVENT_HANDLER_CALLBACK,
        ctypes.c_ulong,
        ctypes.POINTER(CarbonEventTypeSpec),
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    CARBON.InstallEventHandler.restype = ctypes.c_int32
    CARBON.RemoveEventHandler.argtypes = [ctypes.c_void_p]
    CARBON.RemoveEventHandler.restype = ctypes.c_int32
    CARBON.GetEventParameter.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.c_void_p,
    ]
    CARBON.GetEventParameter.restype = ctypes.c_int32
    CARBON.RegisterEventHotKey.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint32,
        CarbonEventHotKeyID,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    CARBON.RegisterEventHotKey.restype = ctypes.c_int32
    CARBON.UnregisterEventHotKey.argtypes = [ctypes.c_void_p]
    CARBON.UnregisterEventHotKey.restype = ctypes.c_int32
    CARBON_AVAILABLE = True
except Exception:
    CARBON = None
    CARBON_AVAILABLE = False


DEFAULT_BLACKLIST = ["Safari", "steam_osx", "iPhone Mirroring", "WeChat"]
APP_VERSION = "1.2.3"
SETTINGS_SCHEMA_VERSION = 2
DEFAULT_START_STOP_HOTKEY = "<cmd>+<ctrl>+<alt>+-"
DEFAULT_MUTE_HOLD_HOTKEY = "<cmd>+<ctrl>+<alt>+="
MAC_KEYCODE_MAP = {
    0: "a",
    1: "s",
    2: "d",
    3: "f",
    4: "h",
    5: "g",
    6: "z",
    7: "x",
    8: "c",
    9: "v",
    11: "b",
    12: "q",
    13: "w",
    14: "e",
    15: "r",
    16: "y",
    17: "t",
    18: "1",
    19: "2",
    20: "3",
    21: "4",
    22: "6",
    23: "5",
    24: "=",
    25: "9",
    26: "7",
    27: "-",
    28: "8",
    29: "0",
    30: "]",
    31: "o",
    32: "u",
    33: "[",
    34: "i",
    35: "p",
    37: "l",
    38: "j",
    39: "'",
    40: "k",
    41: ";",
    42: "\\",
    43: ",",
    44: "/",
    45: "n",
    46: "m",
    47: ".",
    50: "`",
    36: "return",
    48: "tab",
    49: "space",
    51: "backspace",
    53: "esc",
    65: ".",
    67: "*",
    69: "=",
    71: "clear",
    75: "/",
    76: "enter",
    78: "-",
    81: "=",
    82: "0",
    83: "1",
    84: "2",
    85: "3",
    86: "4",
    87: "5",
    88: "6",
    89: "7",
    91: "8",
    92: "9",
    96: "<f5>",
    97: "<f6>",
    98: "<f7>",
    99: "<f3>",
    100: "<f8>",
    101: "<f9>",
    103: "<f11>",
    109: "<f10>",
    111: "<f12>",
    117: "delete",
    118: "<f4>",
    120: "<f2>",
    122: "<f1>",
    123: "left",
    124: "right",
    125: "down",
    126: "up",
}
MODIFIER_DISPLAY_ORDER = ("<cmd>", "<shift>", "<ctrl>", "<alt>")
PRIMARY_KEY_NAME_TO_KEYCODE = {}
for _keycode, _key_name in MAC_KEYCODE_MAP.items():
    PRIMARY_KEY_NAME_TO_KEYCODE.setdefault(_key_name, _keycode)


def resource_dir():
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def app_support_dir():
    path = Path.home() / "Library" / "Application Support" / "Chill Guard"
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        return RESOURCE_DIR
    return path


RESOURCE_DIR = resource_dir()
APP_SUPPORT_DIR = app_support_dir()
LOG_PATH = APP_SUPPORT_DIR / "launch.log"
SETTINGS_PATH = APP_SUPPORT_DIR / "settings.json"


def resolve_model_path(model_name):
    model_path = Path(model_name).expanduser()
    if model_path.is_absolute() and model_path.exists():
        return str(model_path)

    candidate_paths = [
        Path.cwd() / model_name,
        RESOURCE_DIR / model_name,
        APP_SUPPORT_DIR / model_name,
    ]
    for candidate in candidate_paths:
        if candidate.exists():
            return str(candidate)
    return model_name


def append_log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with LOG_PATH.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")
    except OSError:
        pass


def sanitize_blacklist_apps(apps):
    cleaned = []
    seen = set()
    blocked_names = {"chill guard", "chill_guard", "chillguard"}
    for app in apps:
        normalized = app.strip()
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in blocked_names:
            continue
        if lowered in seen:
            continue
        cleaned.append(normalized)
        seen.add(lowered)
    return cleaned or DEFAULT_BLACKLIST.copy()


def migrate_legacy_settings(settings):
    # Unversioned 1.0 files contain real user choices. Only normalize the
    # obsolete zero-person limit; do not infer migrations from valid values.
    if settings.max_allowed_people == 0:
        settings.max_allowed_people = 1
    settings.blacklist_apps = sanitize_blacklist_apps(settings.blacklist_apps)
    return settings


def running_from_bundle():
    return bool(getattr(sys, "frozen", False))


def accessibility_target_label():
    if running_from_bundle():
        return "Chill Guard.app"
    return Path(sys.executable).name


def accessibility_target_path():
    return str(Path(sys.executable).resolve())


def settings_to_dict(settings):
    return {
        "schema_version": SETTINGS_SCHEMA_VERSION,
        "max_allowed_people": settings.max_allowed_people,
        "cooldown_seconds": settings.cooldown_seconds,
        "camera_index": settings.camera_index,
        "trigger_frame_threshold": settings.trigger_frame_threshold,
        "frame_scale": settings.frame_scale,
        "confidence_threshold": settings.confidence_threshold,
        "detect_imgsz": settings.detect_imgsz,
        "camera_width": settings.camera_width,
        "camera_height": settings.camera_height,
        "self_box_expand_x": settings.self_box_expand_x,
        "self_box_expand_y_top": settings.self_box_expand_y_top,
        "self_box_expand_y_bottom": settings.self_box_expand_y_bottom,
        "self_track_max_misses": settings.self_track_max_misses,
        "self_track_min_confidence": settings.self_track_min_confidence,
        "min_risk_box_area_ratio": settings.min_risk_box_area_ratio,
        "far_target_boost_enabled": settings.far_target_boost_enabled,
        "far_target_confidence": settings.far_target_confidence,
        "preview_enabled": settings.preview_enabled,
        "alert_sound_enabled": settings.alert_sound_enabled,
        "blacklist_apps": sanitize_blacklist_apps(settings.blacklist_apps),
        "model_name": settings.model_name,
        "inference_backend": settings.inference_backend,
        "language": settings.language,
        "start_stop_hotkey": settings.start_stop_hotkey,
        "mute_hold_hotkey": settings.mute_hold_hotkey,
        "launch_at_login": settings.launch_at_login,
    }


def save_settings(settings):
    try:
        pending_path = SETTINGS_PATH.with_suffix(".tmp")
        pending_path.write_text(
            json.dumps(settings_to_dict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        pending_path.replace(SETTINGS_PATH)
    except OSError as exc:
        append_log(f"Failed to save settings: {exc}")


def load_settings():
    defaults = GuardSettings()
    if not SETTINGS_PATH.exists():
        return defaults

    try:
        payload = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        append_log(f"Failed to load settings: {exc}")
        return defaults

    if not isinstance(payload, dict):
        append_log("Invalid settings object; using defaults")
        return defaults
    settings = GuardSettings()
    for field_name in settings.__dataclass_fields__:
        if field_name in payload:
            value, default = payload[field_name], getattr(defaults, field_name)
            valid = type(value) is type(default)
            if isinstance(default, float):
                valid = type(value) in (int, float)
            if isinstance(default, list):
                valid = isinstance(value, list) and all(isinstance(item, str) for item in value)
            if valid:
                setattr(settings, field_name, value)
            else:
                append_log(f"Invalid setting type for {field_name}; using default")
    if settings.inference_backend not in ("auto", "coreml", "pytorch"):
        settings.inference_backend = defaults.inference_backend
    if settings.language not in ("zh", "en"):
        settings.language = defaults.language
    if payload.get("schema_version", 0) == 0:
        settings = migrate_legacy_settings(settings)
    return settings


@dataclass
class GuardSettings:
    max_allowed_people: int = 1
    cooldown_seconds: float = 2.0
    camera_index: int = 0
    trigger_frame_threshold: int = 1
    frame_scale: float = 1.0
    confidence_threshold: float = 0.30
    detect_imgsz: int = 1280
    camera_width: int = 1920
    camera_height: int = 1080
    self_box_expand_x: float = 0.28
    self_box_expand_y_top: float = 0.18
    self_box_expand_y_bottom: float = 0.10
    self_track_max_misses: int = 18
    self_track_min_confidence: float = 0.35
    min_risk_box_area_ratio: float = 0.002
    far_target_boost_enabled: bool = False
    far_target_confidence: float = 0.18
    preview_enabled: bool = True
    alert_sound_enabled: bool = True
    blacklist_apps: list[str] = field(default_factory=lambda: DEFAULT_BLACKLIST.copy())
    model_name: str = "yolo26s.pt"
    inference_backend: str = "coreml"
    language: str = "zh"
    start_stop_hotkey: str = DEFAULT_START_STOP_HOTKEY
    mute_hold_hotkey: str = DEFAULT_MUTE_HOLD_HOTKEY
    launch_at_login: bool = False


class GuardRuntime:
    def __init__(self):
        self.settings = load_settings()
        self.stop_event = threading.Event()
        self.thread = None
        self.lock = threading.Lock()
        self.running = False
        self.status = "Standby"
        self.last_trigger_time = 0.0
        self.self_box = None
        self.self_box_misses = 0
        self.latest_preview = None
        self.muted_until_release = False
        self.preview_interval_seconds = 0.12
        self.last_preview_update = 0.0
        self.alert_queue = queue.Queue()
        self.alert_in_flight = False
        self.alert_lock = threading.Lock()
        self.frame_counter = 0
        self.cached_far_detections = []
        self.live_people_count = None
        self.active_backend = None
        self.alert_worker = threading.Thread(target=self._alert_worker_loop, daemon=True)
        self.alert_worker.start()

    def get_settings(self):
        with self.lock:
            return GuardSettings(
                max_allowed_people=self.settings.max_allowed_people,
                cooldown_seconds=self.settings.cooldown_seconds,
                camera_index=self.settings.camera_index,
                trigger_frame_threshold=self.settings.trigger_frame_threshold,
                frame_scale=self.settings.frame_scale,
                confidence_threshold=self.settings.confidence_threshold,
                detect_imgsz=self.settings.detect_imgsz,
                camera_width=self.settings.camera_width,
                camera_height=self.settings.camera_height,
                self_box_expand_x=self.settings.self_box_expand_x,
                self_box_expand_y_top=self.settings.self_box_expand_y_top,
                self_box_expand_y_bottom=self.settings.self_box_expand_y_bottom,
                self_track_max_misses=self.settings.self_track_max_misses,
                self_track_min_confidence=self.settings.self_track_min_confidence,
                min_risk_box_area_ratio=self.settings.min_risk_box_area_ratio,
                far_target_boost_enabled=self.settings.far_target_boost_enabled,
                far_target_confidence=self.settings.far_target_confidence,
                preview_enabled=self.settings.preview_enabled,
                alert_sound_enabled=self.settings.alert_sound_enabled,
                blacklist_apps=self.settings.blacklist_apps.copy(),
                model_name=self.settings.model_name,
                inference_backend=self.settings.inference_backend,
                language=self.settings.language,
                start_stop_hotkey=self.settings.start_stop_hotkey,
                mute_hold_hotkey=self.settings.mute_hold_hotkey,
                launch_at_login=self.settings.launch_at_login,
            )

    def update_settings(self, settings):
        with self.lock:
            self.settings = settings

    def set_preview_enabled(self, enabled):
        with self.lock:
            self.settings.preview_enabled = enabled

    def set_latest_preview(self, frame):
        with self.lock:
            self.latest_preview = frame

    def get_latest_preview(self):
        with self.lock:
            return None if self.latest_preview is None else self.latest_preview.copy()

    def set_muted_until_release(self, muted):
        with self.lock:
            self.muted_until_release = muted

    def is_muted_until_release(self):
        with self.lock:
            return self.muted_until_release

    def can_publish_preview(self):
        now = time.time()
        if now - self.last_preview_update >= self.preview_interval_seconds:
            self.last_preview_update = now
            return True
        return False

    def set_live_people_count(self, count):
        with self.lock:
            self.live_people_count = count

    def get_live_people_count(self):
        with self.lock:
            return self.live_people_count

    def queue_alert(self, blacklist_apps, status_callback):
        with self.alert_lock:
            if self.alert_in_flight:
                return False
            self.alert_in_flight = True
        self.alert_queue.put((sanitize_blacklist_apps(blacklist_apps), status_callback))
        return True

    def _alert_worker_loop(self):
        while True:
            blacklist_apps, status_callback = self.alert_queue.get()
            try:
                ok, error_message = emergency_switch(blacklist_apps)
                if ok:
                    status_callback("Alert action executed")
                else:
                    status_callback(f"Alert failed: {error_message or 'Check Automation permission'}")
            except Exception as exc:
                append_log(f"Alert worker failed: {exc}")
                status_callback(f"Alert failed: {exc}")
            finally:
                with self.alert_lock:
                    self.alert_in_flight = False
                self.alert_queue.task_done()


def clamp(value, lower, upper):
    return max(lower, min(value, upper))


def box_area(box):
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def box_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def expanded_box(box, frame_width, frame_height, settings):
    x1, y1, x2, y2 = box
    width = x2 - x1
    height = y2 - y1

    return (
        clamp(x1 - width * settings.self_box_expand_x, 0, frame_width),
        clamp(y1 - height * settings.self_box_expand_y_top, 0, frame_height),
        clamp(x2 + width * settings.self_box_expand_x, 0, frame_width),
        clamp(y2 + height * settings.self_box_expand_y_bottom, 0, frame_height),
    )


def inset_box(box, frame_width, frame_height, inset_x_ratio=0.12, inset_y_ratio=0.08):
    x1, y1, x2, y2 = box
    width = x2 - x1
    height = y2 - y1
    return (
        clamp(x1 + width * inset_x_ratio, 0, frame_width),
        clamp(y1 + height * inset_y_ratio, 0, frame_height),
        clamp(x2 - width * inset_x_ratio, 0, frame_width),
        clamp(y2 - height * inset_y_ratio, 0, frame_height),
    )


def iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_area = box_area((inter_x1, inter_y1, inter_x2, inter_y2))
    if inter_area <= 0:
        return 0.0

    union_area = box_area(box_a) + box_area(box_b) - inter_area
    return inter_area / union_area if union_area > 0 else 0.0


def intersection_area(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    return box_area((inter_x1, inter_y1, inter_x2, inter_y2))


def select_self_candidate(detections, previous_self_box, frame_width, frame_height, settings):
    scored_candidates = []
    frame_area = frame_width * frame_height

    for detection in detections:
        if detection["confidence"] < settings.self_track_min_confidence:
            continue

        area_score = box_area(detection["box"]) / frame_area
        _, center_y = box_center(detection["box"])
        bottom_score = center_y / frame_height
        stability_score = iou(detection["box"], previous_self_box) if previous_self_box else 0.0
        total_score = area_score * 0.55 + bottom_score * 0.25 + stability_score * 0.20
        scored_candidates.append((total_score, detection))

    if not scored_candidates:
        return None

    scored_candidates.sort(key=lambda item: item[0], reverse=True)
    return scored_candidates[0][1]


def should_keep_buffer_detection(detection, self_box, settings):
    if self_box is None:
        return True

    detection_area = box_area(detection["box"])
    self_area = max(box_area(self_box), 1.0)
    _, center_y = box_center(detection["box"])
    self_x1, self_y1, self_x2, self_y2 = self_box
    self_height = self_y2 - self_y1

    is_smaller_than_self = detection_area <= self_area * 0.42
    is_higher_than_self_base = center_y <= (self_y2 - self_height * 0.10)
    is_upper_half = center_y <= (self_y1 + self_height * 0.58)
    bottom_not_too_low = detection["box"][3] <= (self_y1 + self_height * 0.86)
    confident_enough = detection["confidence"] >= settings.far_target_confidence
    limited_overlap = iou(detection["box"], self_box) <= 0.28

    return (
        is_smaller_than_self
        and is_higher_than_self_base
        and is_upper_half
        and bottom_not_too_low
        and confident_enough
        and limited_overlap
    )


def is_self_fragment_detection(detection, self_box):
    if self_box is None:
        return False

    overlap = iou(detection["box"], self_box)
    if overlap < 0.06:
        return False

    dx1, dy1, dx2, dy2 = detection["box"]
    sx1, sy1, sx2, sy2 = self_box
    self_width = max(1.0, sx2 - sx1)
    self_height = max(1.0, sy2 - sy1)
    self_area = max(1.0, box_area(self_box))
    detection_area = box_area(detection["box"])

    center_x, center_y = box_center(detection["box"])
    self_center_x, _ = box_center(self_box)

    lower_half = center_y >= (sy1 + self_height * 0.50)
    near_self_horizontally = abs(center_x - self_center_x) <= self_width * 0.85
    large_piece = detection_area >= self_area * 0.18
    bottom_aligned = dy2 >= (sy1 + self_height * 0.82)
    starts_inside_self = dy1 >= (sy1 + self_height * 0.12)

    return near_self_horizontally and lower_half and starts_inside_self and (large_piece or bottom_aligned)


def is_same_person_as_self(detection, self_box, self_core_box=None):
    if self_box is None:
        return False

    center_x, center_y = box_center(detection["box"])
    in_self_core = False
    if self_core_box is not None:
        cx1, cy1, cx2, cy2 = self_core_box
        in_self_core = cx1 <= center_x <= cx2 and cy1 <= center_y <= cy2

    overlap_iou = iou(detection["box"], self_box)
    if overlap_iou >= 0.55:
        return True

    self_area = max(1.0, box_area(self_box))
    det_area = max(1.0, box_area(detection["box"]))
    overlap_ratio_to_det = intersection_area(detection["box"], self_box) / det_area
    if overlap_ratio_to_det >= 0.65:
        return True

    # Suppress near-body large false positives (e.g. hand/face posture split into another "person").
    sx1, sy1, sx2, sy2 = self_box
    self_width = max(1.0, sx2 - sx1)
    self_height = max(1.0, sy2 - sy1)
    self_center_x, _ = box_center(self_box)
    near_self_horizontally = abs(center_x - self_center_x) <= self_width * 0.95
    near_self_vertically = center_y >= (sy1 + self_height * 0.20)
    large_like_self = det_area >= self_area * 0.33
    medium_overlap = overlap_iou >= 0.14 or overlap_ratio_to_det >= 0.30
    # Core is only a helper signal. It must still be near + large to be treated as self.
    if near_self_horizontally and near_self_vertically and large_like_self and (medium_overlap or in_self_core):
        return True

    return False


def filter_risk_detections(detections, self_core_box, self_buffer_box, self_box, frame_width, frame_height, settings):
    risk_detections = []
    min_risk_area = frame_width * frame_height * settings.min_risk_box_area_ratio

    for detection in detections:
        if is_self_fragment_detection(detection, self_box):
            continue
        if is_same_person_as_self(detection, self_box, self_core_box):
            continue

        center_x, center_y = box_center(detection["box"])

        if self_buffer_box is not None:
            bx1, by1, bx2, by2 = self_buffer_box
            if bx1 <= center_x <= bx2 and by1 <= center_y <= by2:
                if not should_keep_buffer_detection(detection, self_box, settings):
                    continue

        if box_area(detection["box"]) < min_risk_area:
            continue

        risk_detections.append(detection)

    return risk_detections


def dedupe_detections(detections, iou_threshold=0.45):
    merged = []
    for detection in sorted(detections, key=lambda item: item["confidence"], reverse=True):
        if any(iou(detection["box"], existing["box"]) >= iou_threshold for existing in merged):
            continue
        merged.append(detection)
    return merged


def remap_detection_boxes(detections, scale_x=1.0, scale_y=1.0, offset_x=0.0, offset_y=0.0):
    remapped = []
    for detection in detections:
        x1, y1, x2, y2 = detection["box"]
        remapped.append(
            {
                "box": (
                    x1 * scale_x + offset_x,
                    y1 * scale_y + offset_y,
                    x2 * scale_x + offset_x,
                    y2 * scale_y + offset_y,
                ),
                "confidence": detection["confidence"],
            }
        )
    return remapped


def emergency_switch(blacklist_apps):
    safe_blacklist = sanitize_blacklist_apps(blacklist_apps)
    applescript_list = "{" + ", ".join([f'"{app}"' for app in safe_blacklist]) + "}"
    apple_script = f"""
    tell application "System Events"
        set blacklist to {applescript_list}
        repeat with appName in blacklist
            if exists (process appName) then
                try
                    set visible of process appName to false
                end try
            end if
        end repeat
    end tell
    """
    completed = subprocess.run(
        ["osascript", "-e", apple_script],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        append_log(f"AppleScript failed: {completed.stderr.strip() or 'unknown error'}")
    return completed.returncode == 0, completed.stderr.strip()


def play_alert_sound():
    try:
        NSBeep()
    except Exception as exc:
        append_log(f"Alert sound failed: {exc}")


def has_accessibility_permission():
    try:
        return bool(AXIsProcessTrusted())
    except Exception as exc:
        append_log(f"Accessibility check failed: {exc}")
        return False


def request_accessibility_permission():
    try:
        return bool(AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: True}))
    except Exception as exc:
        append_log(f"Accessibility prompt failed: {exc}")
        return False


def app_bundle_path():
    executable_path = Path(sys.executable).resolve()
    if getattr(sys, "frozen", False) and executable_path.name == "Chill Guard":
        return executable_path.parents[2]
    return (RESOURCE_DIR / "dist" / "Chill Guard.app").resolve()


def set_launch_at_login(enabled):
    app_path = str(app_bundle_path()).replace('"', '\\"')
    if enabled:
        apple_script = f'''
        tell application "System Events"
            if exists login item "Chill Guard" then
                delete login item "Chill Guard"
            end if
            make login item at end with properties {{name:"Chill Guard", path:"{app_path}", hidden:false}}
        end tell
        '''
    else:
        apple_script = '''
        tell application "System Events"
            if exists login item "Chill Guard" then
                delete login item "Chill Guard"
            end if
        end tell
        '''

    completed = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Unable to update launch-at-login setting")


class StatusBarController(NSObject):
    def initWithApp_(self, app):
        self = objc.super(StatusBarController, self).init()
        if self is None:
            return None
        self.app = app
        self.dock_menu = None
        self.menu = None
        self.toggle_monitoring_item = None
        return self

    def setup(self):
        menu = NSMenu.alloc().init()
        menu.setTitle_("Chill Guard")
        self.menu = menu
        show_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Show Main Window", "showWindow:", "")
        show_item.setTarget_(self)
        self.show_item = show_item
        menu.addItem_(show_item)
        self.toggle_monitoring_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Start Monitoring", "toggleMonitoring:", "")
        self.toggle_monitoring_item.setTarget_(self)
        menu.addItem_(self.toggle_monitoring_item)
        menu.addItem_(NSMenuItem.separatorItem())
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Quit", "quitApp:", "")
        quit_item.setTarget_(self)
        self.quit_item = quit_item
        menu.addItem_(quit_item)

        self.dock_menu = menu
        app = NSApplication.sharedApplication()
        if hasattr(app, "setDockMenu_"):
            app.setDockMenu_(menu)
        else:
            app.setDelegate_(self)
        self.refresh_menu_state()

    def showWindow_(self, _sender):
        self.app.enqueue_ui_task(self.app.show_main_window)

    def toggleMonitoring_(self, _sender):
        self.app.enqueue_ui_task(self.app.toggle_monitoring_from_hotkey)

    def quitApp_(self, _sender):
        self.app.enqueue_ui_task(self.app.quit_application)

    def applicationDockMenu_(self, _sender):
        self.refresh_menu_state()
        return self.dock_menu

    def refresh_menu_state(self):
        language = Language(self.app.runtime.get_settings().language)
        if getattr(self, "show_item", None) is not None:
            self.show_item.setTitle_(language.text("Show Main Window"))
        if getattr(self, "quit_item", None) is not None:
            self.quit_item.setTitle_(language.text("Quit"))
        if self.toggle_monitoring_item is not None:
            self.toggle_monitoring_item.setTitle_(language.text("Stop Monitoring" if self.app.runtime.running else "Start Monitoring"))


def draw_debug_frame(frame, detections, self_box, self_core_box, self_buffer_box, risk_detections, cooldown_left, people_count=None):
    debug_frame = frame.copy()

    if self_box is not None:
        x1, y1, x2, y2 = [int(value) for value in self_box]
        cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 180, 255), 2)
        cv2.putText(
            debug_frame,
            "SELF",
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 180, 255),
            2,
        )

    for detection in risk_detections:
        x1, y1, x2, y2 = [int(value) for value in detection["box"]]
        cv2.rectangle(debug_frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.putText(
            debug_frame,
            f"RISK {detection['confidence']:.2f}",
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 255),
            2,
        )

    rendered_people = people_count if people_count is not None else len(detections)
    cv2.putText(
        debug_frame,
        f"people={rendered_people} risk_targets={len(risk_detections)} cooldown={cooldown_left:.1f}s",
        (15, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (50, 255, 50),
        2,
    )
    return debug_frame


def monitor_loop(runtime, status_callback):
    settings = runtime.get_settings()
    runtime.last_trigger_time = 0.0
    runtime.self_box = None
    runtime.self_box_misses = 0
    cap = None
    failed = False

    try:
        status_callback("Loading model...")
        def load_detector(current_settings):
            detector = create_detector(
                resolve_model_path(current_settings.model_name),
                backend=current_settings.inference_backend,
                imgsz=current_settings.detect_imgsz,
                model_dirs=(RESOURCE_DIR / ".models", RESOURCE_DIR / "models", APP_SUPPORT_DIR / "models"),
            )
            if detector.notice:
                append_log(detector.notice)
            runtime.active_backend = detector.description
            status_callback(f"Model ready: {detector.description} / camera {current_settings.camera_index}"
                            + (f". {detector.notice}" if detector.notice else ""))
            return detector

        model = load_detector(settings)
        model_config = (settings.model_name, settings.inference_backend, settings.detect_imgsz)

        cap = cv2.VideoCapture(settings.camera_index, cv2.CAP_AVFOUNDATION)
        if not cap.isOpened():
            raise RuntimeError("Cannot open the camera. Check permissions, the selected index, or whether another app is using it.")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.camera_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.camera_height)
        status_callback(f"Monitoring: {model.description} / camera {settings.camera_index} connected"
                        + (f". {model.notice}" if model.notice else ""))

        consecutive_count = 0

        while not runtime.stop_event.is_set():
            settings = runtime.get_settings()
            updated_config = (settings.model_name, settings.inference_backend, settings.detect_imgsz)
            if updated_config != model_config:
                model = load_detector(settings)
                model_config = updated_config
                consecutive_count = 0
                runtime.cached_far_detections = []
            runtime.frame_counter += 1
            try:
                ret, frame = cap.read()
            except cv2.error as exc:
                raise RuntimeError(f"Failed to read a camera frame: {exc}") from exc
            if not ret:
                raise RuntimeError("Failed to read a camera frame. Check the device connection state.")

            frame = cv2.flip(frame, 1)
            small_frame = cv2.resize(frame, (0, 0), fx=settings.frame_scale, fy=settings.frame_scale)

            previous_backend = model.description
            detections = model.detect(small_frame, settings.confidence_threshold, settings.detect_imgsz)

            if settings.far_target_boost_enabled and runtime.frame_counter % 4 == 0:
                frame_height_full, frame_width_full = frame.shape[:2]
                roi_x1 = int(frame_width_full * 0.22)
                roi_x2 = int(frame_width_full * 0.78)
                roi_y1 = int(frame_height_full * 0.22)
                roi_y2 = int(frame_height_full * 0.86)

                if roi_x2 > roi_x1 and roi_y2 > roi_y1:
                    far_roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
                    far_detections = model.detect(
                        far_roi, min(settings.confidence_threshold, settings.far_target_confidence),
                        max(settings.detect_imgsz, 1280))
                    remapped_far = remap_detection_boxes(
                        far_detections,
                        scale_x=settings.frame_scale,
                        scale_y=settings.frame_scale,
                        offset_x=roi_x1 * settings.frame_scale,
                        offset_y=roi_y1 * settings.frame_scale,
                    )
                    runtime.cached_far_detections = remapped_far
            if settings.far_target_boost_enabled and runtime.cached_far_detections:
                detections += runtime.cached_far_detections
            elif not settings.far_target_boost_enabled:
                runtime.cached_far_detections = []
            if model.description != previous_backend:
                runtime.active_backend = model.description
                append_log(model.notice or model.description)
                status_callback(f"Monitoring: {model.description}. {model.notice or ''}")
            # Remove lower-confidence duplicates before they can win the self
            # candidate score and suppress a separate, valid person.
            detections = dedupe_detections(detections)

            frame_height, frame_width = small_frame.shape[:2]

            self_candidate = select_self_candidate(
                detections,
                runtime.self_box,
                frame_width,
                frame_height,
                settings,
            )
            if self_candidate is not None:
                runtime.self_box = self_candidate["box"]
                runtime.self_box_misses = 0
            else:
                runtime.self_box_misses += 1
                if runtime.self_box_misses > settings.self_track_max_misses:
                    runtime.self_box = None

            self_buffer_box = (
                expanded_box(runtime.self_box, frame_width, frame_height, settings)
                if runtime.self_box is not None
                else None
            )
            self_core_box = (
                inset_box(runtime.self_box, frame_width, frame_height)
                if runtime.self_box is not None
                else None
            )
            risk_detections = filter_risk_detections(
                detections,
                self_core_box,
                self_buffer_box,
                runtime.self_box,
                frame_width,
                frame_height,
                settings,
            )
            risk_detections = dedupe_detections(risk_detections)

            current_time = time.time()
            cooldown_left = max(0.0, settings.cooldown_seconds - (current_time - runtime.last_trigger_time))

            # Preview, live count, and alerts share exactly the same eligible targets.
            self_present = any(is_same_person_as_self(item, runtime.self_box, self_core_box)
                               for item in detections) if runtime.self_box is not None else False
            total_people = int(self_present) + len(risk_detections)
            runtime.set_live_people_count(total_people)
            over_people_limit = total_people > settings.max_allowed_people
            # Respect the configured people limit. Risk boxes are still shown in preview/status,
            # but they should not bypass the user's allowed-people setting.
            should_trigger_alert = over_people_limit

            if should_trigger_alert:
                consecutive_count += 1
                if (
                    consecutive_count >= settings.trigger_frame_threshold
                    and current_time - runtime.last_trigger_time > settings.cooldown_seconds
                ):
                    if runtime.is_muted_until_release():
                        runtime.last_trigger_time = current_time
                        status_callback(f"Muted: detected {len(risk_detections)} risk targets")
                        continue

                    if settings.alert_sound_enabled:
                        play_alert_sound()

                    runtime.last_trigger_time = current_time
                    queued = runtime.queue_alert(settings.blacklist_apps, status_callback)
                    if queued:
                        status_callback(f"Alert triggered: current frame {total_people} people / risk {len(risk_detections)}")
                    else:
                        status_callback(f"Alert already in progress: current frame {total_people} people / risk {len(risk_detections)}")
            else:
                consecutive_count = 0

            if settings.preview_enabled and runtime.can_publish_preview():
                debug_frame = draw_debug_frame(
                    small_frame,
                    detections,
                    runtime.self_box,
                    self_core_box,
                    self_buffer_box,
                    risk_detections,
                    cooldown_left,
                    people_count=total_people,
                )
                runtime.set_latest_preview(debug_frame)
            elif not settings.preview_enabled:
                runtime.set_latest_preview(None)

    except Exception as exc:
        failed = True
        append_log(f"Monitor loop error: {exc}")
        status_callback(f"Monitoring stopped: {exc}")
    finally:
        runtime.running = False
        runtime.stop_event.clear()
        runtime.set_latest_preview(None)
        runtime.set_live_people_count(None)
        runtime.cached_far_detections = []
        if cap is not None:
            cap.release()
        if not failed:
            status_callback("Monitoring stopped")


class ChillGuardApp:
    persist_settings = staticmethod(save_settings)
    serialized_settings = staticmethod(settings_to_dict)

    def __init__(self, root):
        self.root = root
        self.root.title("Chill Guard Console")
        self.root.geometry("760x460")
        self.root.minsize(760, 460)
        self.runtime = GuardRuntime()
        self.ui_task_queue = queue.Queue()
        self.ui_task_polling = True
        self.status_var = tk.StringVar(value="Standby")
        self.preview_image = None
        self.hotkey_event_tap = None
        self.hotkey_run_loop = None
        self.hotkey_thread = None
        self.hotkey_event_tap_callback = None
        self.hotkey_global_monitor = None
        self.hotkey_global_monitor_callback = None
        self.hotkey_local_runtime_monitor = None
        self.hotkey_local_runtime_monitor_callback = None
        self.hotkey_tap_source_name = None
        self.hotkey_listener_sources = set()
        self.hotkey_listener_active = False
        self.last_hotkey_attach_attempt = 0.0
        self.last_hotkey_permission = None
        self.hotkey_event_counter = 0
        self.last_hotkey_event_signature = None
        self.last_hotkey_event_timestamp = 0.0
        self.current_hotkey_modifiers = set()
        self.current_hotkey_keys = set()
        self.carbon_hotkey_handler_callback = None
        self.carbon_hotkey_handler_ref = None
        self.carbon_hotkey_target = None
        self.carbon_hotkey_refs = {}
        self.carbon_hotkey_roles = {}
        self.suppress_status_reset = False
        self.hotkey_capture_target = None
        self.hotkey_capture_modifiers = set()
        self.hotkey_capture_keycode = None
        self.hotkey_capture_monitor = None
        self.hotkey_capture_timeout_id = None
        self.default_settings = GuardSettings()
        self.status_bar_controller = None
        self.hotkey_status_var = tk.StringVar(value="Checking global hotkey permission...")
        self.launch_at_login_var = tk.BooleanVar(value=False)
        self.parameters_expanded_var = tk.BooleanVar(value=False)
        self.hotkeys_expanded_var = tk.BooleanVar(value=False)
        self.startup_expanded_var = tk.BooleanVar(value=False)
        self.guide_expanded_var = tk.BooleanVar(value=False)
        self.testing_expanded_var = tk.BooleanVar(value=False)
        self.parameters_frame = None
        self.parameters_toggle_button = None
        self.hotkeys_toggle_button = None
        self.startup_toggle_button = None
        self.guide_toggle_button = None
        self.testing_toggle_button = None
        self.preview_row = None
        self.blacklist_chip_container = None
        self.blacklist_helper_var = tk.StringVar(value="")
        self.status_caption_var = tk.StringVar(value="Status: Standby")
        self.status_detail_var = tk.StringVar(value="Ready. Start monitoring when you are set.")
        self.status_pill_var = tk.StringVar(value="Standby")
        self.status_caption_label = None
        self.status_detail_label = None
        self.status_pill_label = None
        self.status_dot = None
        self.hotkey_hint_var = tk.StringVar(value="")
        self.settings_summary_var = tk.StringVar(value="")
        self.hotkey_compact_var = tk.StringVar(value="Checking permissions")
        self.startup_summary_var = tk.StringVar(value="")
        self.preview_chip_people_var = tk.StringVar(value="People --")
        self.preview_chip_limit_var = tk.StringVar(value="Allowed 1")
        self.preview_chip_state_var = tk.StringVar(value="Standby")
        self.latest_people_count = None
        self.monitor_mode_var = tk.StringVar(value="basic")
        self.monitor_mode_hint_var = tk.StringVar(value="")
        self.monitor_basic_frame = None
        self.monitor_advanced_frame = None
        self.collapsible_sections = {}

        self.setup_theme()
        self.build_form()
        self.populate_form_from_settings(self.runtime.get_settings())
        self.root.after(16, self.drain_ui_task_queue)
        self.setup_status_bar()
        self.start_hotkey_listener()
        self.refresh_hotkey_status()
        self.refresh_preview()
        self.root.protocol("WM_DELETE_WINDOW", self.hide_main_window)
        self.root.bind("<Map>", self.on_window_mapped, add="+")
        self.root.bind("<Unmap>", self.on_window_unmapped, add="+")
        self.root.bind("<Destroy>", self.on_window_destroyed, add="+")

    def build_form(self):
        build_workspace(self, APP_VERSION)

    def set_status(self, message):
        append_log(f"STATUS: {message}")
        self.status_var.set(message)
        self.status_caption_var.set(f"Status: {message}")
        self.status_detail_var.set(self.status_detail_for_message(message))
        self.update_status_indicator(message)
        self.update_runtime_chips(message)
        self.update_status_layout()
        self.update_status_bar_controls()

    def update_status_layout(self, _event=None):
        # The workspace owns wrapping and responsive card sizes.
        return

    def status_detail_for_message(self, message):
        if "Monitoring:" in message or "Starting monitoring" in message:
            return "Camera and model are active and analyzing the scene."
        if "Alert triggered" in message:
            return "Risk condition detected. Chill Guard is executing the protection flow."
        if "Muted" in message or "mute" in message.lower():
            return "Temporary mute is active. Release the hotkey to resume alerts."
        if "failed" in message.lower() or "stopped" in message.lower():
            return "This monitoring session is not running. Check permissions or device state."
        if "Settings applied" in message:
            return "Settings were saved and will be reused next launch."
        return "Ready. Start monitoring when you are set."

    def update_status_indicator(self, message):
        if self.status_dot is None:
            return
        if "Alert triggered" in message:
            color = "#ef4444"
        elif "Monitoring:" in message or "Starting monitoring" in message:
            color = "#22c55e"
        elif "failed" in message.lower() or "stopped" in message.lower():
            color = "#f59e0b"
        else:
            color = "#60a5fa"
        self.status_dot.delete("all")
        self.status_dot.create_oval(2, 2, 12, 12, fill=color, outline="")

    def enqueue_ui_task(self, callback, *args, **kwargs):
        self.ui_task_queue.put((callback, args, kwargs))

    def drain_ui_task_queue(self):
        if not self.ui_task_polling:
            return
        processed = 0
        while processed < 200:
            try:
                callback, args, kwargs = self.ui_task_queue.get_nowait()
            except queue.Empty:
                break
            try:
                callback(*args, **kwargs)
            except Exception as exc:
                append_log(f"UI task failed: {exc}")
            processed += 1
        try:
            self.root.after(16, self.drain_ui_task_queue)
        except tk.TclError:
            pass

    def async_status(self, message):
        self.enqueue_ui_task(self.set_status, message)

    def setup_theme(self):
        setup_workspace_theme(self)

    def setup_status_bar(self):
        try:
            self.status_bar_controller = StatusBarController.alloc().initWithApp_(self)
            self.status_bar_controller.setup()
            self.update_status_bar_controls()
            append_log("Status bar setup completed")
        except Exception as exc:
            append_log(f"Status bar setup failed: {exc}")

    def update_status_bar_controls(self):
        if self.status_bar_controller is None:
            return
        try:
            self.status_bar_controller.refresh_menu_state()
        except Exception as exc:
            append_log(f"Status bar refresh failed: {exc}")

    def toggle_parameters_section(self):
        self.show_monitor_advanced_view()

    def update_parameters_section_visibility(self):
        self.show_monitor_basic_view()

    def show_monitor_basic_view(self):
        if self.monitor_basic_frame is not None:
            self.monitor_advanced_frame.grid_remove()
            self.monitor_basic_frame.grid()
        if self.parameters_toggle_button is not None:
            self.parameters_toggle_button.configure(text="Advanced", command=self.show_monitor_advanced_view)
        self.monitor_mode_var.set("basic")
        self.monitor_mode_hint_var.set("Basic settings: frequent parameters and model configuration")
        self.refresh_form_summaries()

    def show_monitor_advanced_view(self):
        if self.monitor_advanced_frame is not None:
            self.monitor_basic_frame.grid_remove()
            self.monitor_advanced_frame.grid()
        if self.parameters_toggle_button is not None:
            self.parameters_toggle_button.configure(text="Back to Basics", command=self.show_monitor_basic_view)
        self.monitor_mode_var.set("advanced")
        self.monitor_mode_hint_var.set("Advanced settings: ignore zones, tracking tolerance, and long-range boost")
        self.refresh_form_summaries()

    def switch_settings_panel(self, name):
        if not hasattr(self, "panel_frames") or name not in self.panel_frames:
            return
        for key, frame in self.panel_frames.items():
            frame.grid() if key == name else frame.grid_remove()
        self.active_settings_panel = name
        if name == "parameters":
            if self.monitor_mode_var.get() == "advanced":
                self.show_monitor_advanced_view()
            else:
                self.show_monitor_basic_view()
        if getattr(self, "ui", None) is not None:
            self.ui.select_page(name)
            self.ui.refresh()

    def toggle_section(self, name):
        section = self.collapsible_sections.get(name)
        if section is None:
            return
        section["var"].set(not section["var"].get())
        self.update_section_visibility(name)

    def update_section_visibility(self, name):
        section = self.collapsible_sections.get(name)
        if section is None:
            return
        body = section["body"]
        button = section["button"]
        if section["var"].get():
            if body.winfo_manager() != "pack":
                body.pack(fill="x", pady=(14, 0))
            button.configure(text="Collapse")
        else:
            body.pack_forget()
            button.configure(text="Expand")

    def update_all_section_visibility(self):
        for name in self.collapsible_sections:
            self.update_section_visibility(name)

    def refresh_form_summaries(self):
        self.update_runtime_chips()
        if getattr(self, "ui", None) is not None:
            self.ui.refresh()

    def update_runtime_chips(self, message=None):
        text = message if message is not None else self.status_var.get()
        if text is None:
            text = ""

        live_people_count = self.runtime.get_live_people_count() if self.runtime is not None else None
        if live_people_count is not None:
            self.latest_people_count = int(live_people_count)
        else:
            match = re.search(r"current frame\s*(\d+)\s*people", text, re.IGNORECASE)
            if match:
                self.latest_people_count = int(match.group(1))
            elif any(keyword in text for keyword in ("Standby", "stopped", "failed")):
                self.latest_people_count = None

        if self.latest_people_count is None:
            self.preview_chip_people_var.set("People --")
        else:
            self.preview_chip_people_var.set(f"People {self.latest_people_count}")

        if self.entries and "max_allowed_people" in self.entries:
            limit_text = self.entries["max_allowed_people"].get().strip() or "1"
            self.preview_chip_limit_var.set(f"Allowed {limit_text}")

        if text.startswith("Monitoring stopped:") or ("failed" in text.lower() and "Using PyTorch" not in text):
            self.preview_chip_state_var.set("Error")
            self.status_pill_var.set("Error")
        elif self.runtime.is_muted_until_release():
            self.preview_chip_state_var.set("Muted")
            self.status_pill_var.set("Muted")
        elif text.startswith(("Alert triggered", "Alert already in progress")):
            self.preview_chip_state_var.set("Alerting")
            self.status_pill_var.set("Alert")
        elif self.runtime.running and text.startswith(("Starting monitoring", "Loading model", "Model ready:")):
            self.preview_chip_state_var.set("Starting")
            self.status_pill_var.set("Starting")
        elif self.runtime.running:
            self.preview_chip_state_var.set("Monitoring")
            self.status_pill_var.set("Running")
        else:
            self.preview_chip_state_var.set("Standby")
            self.status_pill_var.set("Standby")
        self.update_status_layout()
        if getattr(self, "ui", None) is not None:
            self.ui.refresh()

    def get_blacklist_items(self):
        return [
            line.strip()
            for line in self.blacklist_text.get("1.0", "end").splitlines()
            if line.strip()
        ]

    def render_blacklist_chips(self):
        if getattr(self, "ui", None) is not None:
            self.ui.refresh()

    def on_blacklist_text_modified(self, _event=None):
        self.blacklist_text.edit_modified(False)
        self.render_blacklist_chips()
        self.refresh_form_summaries()

    def refresh_hotkey_status(self):
        permission_granted = has_accessibility_permission()
        listener_thread_alive = self.hotkey_thread is not None and self.hotkey_thread.is_alive()
        now = time.time()
        if not self.hotkey_listener_active and not listener_thread_alive:
            # Use actual event-tap attach result as source of truth; permission API can lag or misreport.
            if permission_granted or now - self.last_hotkey_attach_attempt >= 10.0:
                self.start_hotkey_listener()
        self.last_hotkey_permission = permission_granted

        target_label = accessibility_target_label()
        target_path = accessibility_target_path()
        running_temp_bundle = running_from_bundle() and "/var/folders/" in target_path

        if self.hotkey_listener_active:
            source_label = self.describe_hotkey_listener_sources()
            if permission_granted:
                self.hotkey_status_var.set(f"Global hotkeys enabled ({source_label})")
                self.hotkey_hint_var.set(f"Current authorized target: {target_label}")
            else:
                if running_temp_bundle:
                    self.hotkey_status_var.set("This test bundle is in a temporary directory and does not have Accessibility permission yet")
                    self.hotkey_hint_var.set(f"Re-enable this exact path in Accessibility: {app_bundle_path()}")
                else:
                    self.hotkey_status_var.set("The listener is attached, but macOS still does not consider this app authorized")
                    self.hotkey_hint_var.set(f"Confirm Accessibility is enabled for this app: {app_bundle_path()}")
        elif permission_granted:
            self.hotkey_status_var.set("Accessibility is authorized. Retrying global listener attach")
            self.hotkey_hint_var.set(f"Current authorized target: {target_label} (if it still fails, click “Retry Listener Attach”)")
        else:
            if running_temp_bundle:
                self.hotkey_status_var.set("This test bundle is in a temporary directory and needs its own Accessibility permission")
                self.hotkey_hint_var.set(f"Confirm the temporary test app is checked: {app_bundle_path()}")
            elif running_from_bundle():
                self.hotkey_status_var.set("Global hotkeys unavailable: grant Accessibility permission to Chill Guard.app")
                self.hotkey_hint_var.set(f"Confirm the checked app is this one: {app_bundle_path()}")
            else:
                self.hotkey_status_var.set("Global hotkeys unavailable: source mode requires Accessibility permission for the current Python")
                self.hotkey_hint_var.set(f"Enable this target in Accessibility: {target_path}")
        self.refresh_form_summaries()
        self.root.after(2500, self.refresh_hotkey_status)

    def retry_hotkey_listener(self):
        permission_granted = has_accessibility_permission()
        self.restart_hotkey_listener(force=True)
        self.refresh_hotkey_status()
        if permission_granted:
            self.set_status("Retried global hotkey listener attach")
        else:
            self.set_status("Retried listener attach. If it still fails, confirm Accessibility is enabled for this app")

    def open_accessibility_settings(self):
        request_accessibility_permission()
        subprocess.run(
            ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"],
            check=False,
        )
        if running_from_bundle():
            self.set_status("Opened Accessibility settings. Enable Chill Guard there")
        else:
            self.set_status("Opened Accessibility settings. Enable Python or Terminal there")

    def show_main_window(self):
        append_log("show_main_window requested")
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_main_window(self):
        append_log("hide_main_window requested")
        self.root.withdraw()
        self.set_status("Main window hidden. Reopen it from the menu bar icon")

    def on_window_mapped(self, event):
        if event.widget is self.root:
            append_log("Main window mapped")

    def on_window_unmapped(self, event):
        if event.widget is self.root:
            append_log("Main window unmapped")

    def on_window_destroyed(self, event):
        if event.widget is self.root:
            append_log("Main window destroyed")

    def on_launch_at_login_toggled(self):
        try:
            set_launch_at_login(self.launch_at_login_var.get())
            self.apply_settings()
            self.refresh_form_summaries()
            self.set_status("Launch-at-login setting updated")
        except RuntimeError as exc:
            self.launch_at_login_var.set(not self.launch_at_login_var.get())
            messagebox.showerror(self.ui.t("Launch-at-login update failed"), self.ui.language.system(str(exc)), parent=self.root)

    def test_alert_sound(self):
        play_alert_sound()
        self.set_status("Played the test alert sound")

    def test_temporary_mute(self):
        self.runtime.set_muted_until_release(True)
        self.set_status("Temporary mute test enabled. It will auto-clear in 5 seconds")
        self.root.after(5000, self.end_temporary_mute_test)

    def end_temporary_mute_test(self):
        self.runtime.set_muted_until_release(False)
        self.set_status("Temporary mute test cleared")

    def test_emergency_switch(self):
        settings = self.runtime.get_settings()
        ok, error_message = emergency_switch(settings.blacklist_apps)
        if ok:
            self.set_status("Test app hide executed")
        else:
            self.set_status(f"Test app hide failed: {error_message or 'Check Automation permission'}")

    def parse_settings(self):
        previous = self.runtime.get_settings()
        def saved_hotkey(variable, name):
            display, original = variable.get().strip(), getattr(previous, name)
            pending = getattr(self, "pending_hotkeys", {}).get(name)
            if pending is not None:
                return pending
            return original if display == self.format_hotkey_display(original) else self.normalize_hotkey(display)
        try:
            settings = GuardSettings(
                max_allowed_people=int(self.entries["max_allowed_people"].get().strip()),
                cooldown_seconds=float(self.entries["cooldown_seconds"].get().strip()),
                camera_index=int(self.entries["camera_index"].get().strip()),
                trigger_frame_threshold=int(self.entries["trigger_frame_threshold"].get().strip()),
                frame_scale=float(self.entries["frame_scale"].get().strip()),
                confidence_threshold=float(self.entries["confidence_threshold"].get().strip()),
                detect_imgsz=int(self.entries["detect_imgsz"].get().strip()),
                self_box_expand_x=float(self.entries["self_box_expand_x"].get().strip()),
                self_box_expand_y_top=float(self.entries["self_box_expand_y_top"].get().strip()),
                self_box_expand_y_bottom=float(self.entries["self_box_expand_y_bottom"].get().strip()),
                self_track_max_misses=int(self.entries["self_track_max_misses"].get().strip()),
                self_track_min_confidence=float(self.entries["self_track_min_confidence"].get().strip()),
                min_risk_box_area_ratio=float(self.entries["min_risk_box_area_ratio"].get().strip()),
                far_target_boost_enabled=self.far_target_boost_var.get(),
                far_target_confidence=float(self.entries["far_target_confidence"].get().strip()),
                preview_enabled=self.preview_var.get(),
                alert_sound_enabled=self.alert_sound_var.get(),
                blacklist_apps=[
                    line.strip()
                    for line in self.blacklist_text.get("1.0", "end").splitlines()
                    if line.strip()
                ],
                model_name=self.model_var.get().strip() or "yolo26s.pt",
                inference_backend=self.backend_var.get(),
                language=previous.language,
                camera_width=previous.camera_width,
                camera_height=previous.camera_height,
                start_stop_hotkey=saved_hotkey(self.start_stop_hotkey_var, "start_stop_hotkey"),
                mute_hold_hotkey=saved_hotkey(self.mute_hold_hotkey_var, "mute_hold_hotkey"),
                launch_at_login=self.launch_at_login_var.get(),
            )
        except ValueError as exc:
            raise ValueError("Some parameters are invalid. Check the numeric fields.") from exc

        if not all(math.isfinite(getattr(settings, name)) for name in self.entries):
            raise ValueError("Some parameters are invalid. Check the numeric fields.")
        if not 0.1 <= settings.frame_scale <= 1.0:
            raise ValueError("Frame scale should be between 0.1 and 1.0.")
        if not 0.05 <= settings.confidence_threshold <= 1.0:
            raise ValueError("Confidence threshold should be between 0.05 and 1.0.")
        if not 320 <= settings.detect_imgsz <= 1600:
            raise ValueError("Detect size should be between 320 and 1600.")
        if not 0.05 <= settings.far_target_confidence <= 1.0:
            raise ValueError("Long-range boost threshold should be between 0.05 and 1.0.")
        if settings.trigger_frame_threshold < 1:
            raise ValueError("Trigger frames must be at least 1.")
        if settings.camera_index < 0:
            raise ValueError("Camera index cannot be negative.")
        if settings.cooldown_seconds < 0:
            raise ValueError("Cooldown cannot be negative.")
        if min(settings.self_box_expand_x, settings.self_box_expand_y_top, settings.self_box_expand_y_bottom) < 0:
            raise ValueError("Ignore-zone expansions cannot be negative.")
        if not 0.05 <= settings.self_track_min_confidence <= 1.0:
            raise ValueError("Tracking confidence should be between 0.05 and 1.0.")
        if settings.self_track_max_misses < 0:
            raise ValueError("Missed-frame tolerance cannot be negative.")
        if not 0 <= settings.min_risk_box_area_ratio <= 1:
            raise ValueError("Risk-box area ratio should be between 0 and 1.")
        if settings.max_allowed_people < 1:
            raise ValueError("Allowed people must be at least 1, including the main user.")
        if settings.inference_backend not in ("auto", "coreml", "pytorch"):
            raise ValueError("Choose auto, coreml, or pytorch inference.")
        if not settings.blacklist_apps:
            raise ValueError("Blacklist cannot be empty. Keep at least one app name.")
        if not settings.start_stop_hotkey:
            raise ValueError("Start/stop hotkey cannot be empty.")
        if not settings.mute_hold_hotkey:
            raise ValueError("Hold-to-mute hotkey cannot be empty.")

        return settings

    def apply_settings(self):
        try:
            settings = self.parse_settings()
        except ValueError as exc:
            messagebox.showerror(self.ui.t("Invalid Settings"), self.ui.language.system(str(exc)), parent=self.root)
            return False

        previous_settings = self.runtime.get_settings()
        self.runtime.update_settings(settings)
        save_settings(settings)
        self.pending_hotkeys = {}
        hotkey_changed = (
            previous_settings.start_stop_hotkey != settings.start_stop_hotkey
            or previous_settings.mute_hold_hotkey != settings.mute_hold_hotkey
        )
        if hotkey_changed:
            self.restart_hotkey_listener()
        self.refresh_form_summaries()
        self.set_status("Settings applied")
        return True

    def start_monitoring(self):
        if self.runtime.running:
            self.set_status("Monitoring is already running")
            return

        if not self.apply_settings():
            return

        self.runtime.stop_event.clear()
        self.runtime.set_live_people_count(None)
        self.runtime.running = True
        self.runtime.thread = threading.Thread(
            target=monitor_loop,
            args=(self.runtime, self.async_status),
            daemon=True,
        )
        self.runtime.thread.start()
        self.set_status("Starting monitoring...")

    def stop_monitoring(self):
        if not self.runtime.running:
            self.set_status("Monitoring is not running")
            return

        self.runtime.stop_event.set()
        self.runtime.set_live_people_count(None)
        self.set_status("Stopping monitoring...")

    def on_preview_toggled(self):
        self.runtime.set_preview_enabled(self.preview_var.get())
        save_settings(self.runtime.get_settings())
        self.refresh_form_summaries()
        if self.preview_var.get():
            self.set_status("Preview enabled")
        else:
            self.runtime.set_latest_preview(None)
            self.set_status("Preview disabled")

    def toggle_preview_from_status_menu(self):
        new_state = not self.preview_var.get()
        self.preview_var.set(new_state)
        settings = self.runtime.get_settings()
        settings.preview_enabled = new_state
        self.runtime.update_settings(settings)
        if not new_state:
            self.runtime.set_latest_preview(None)
        save_settings(settings)
        self.refresh_form_summaries()
        self.set_status("Preview enabled" if new_state else "Preview disabled")

    def toggle_alert_sound_from_status_menu(self):
        new_state = not self.alert_sound_var.get()
        self.alert_sound_var.set(new_state)
        settings = self.runtime.get_settings()
        settings.alert_sound_enabled = new_state
        self.runtime.update_settings(settings)
        save_settings(settings)
        self.refresh_form_summaries()
        self.set_status("Alert sound enabled" if new_state else "Alert sound disabled")

    def normalize_hotkey(self, hotkey_text):
        normalized = hotkey_text.strip().lower().replace(" ", "")
        if not normalized:
            return ""
        alias_map = {
            "cmd": "<cmd>",
            "command": "<cmd>",
            "shift": "<shift>",
            "ctrl": "<ctrl>",
            "control": "<ctrl>",
            "alt": "<alt>",
            "option": "<alt>",
            "escape": "esc",
        }
        modifiers = set()
        primary_key = None
        for raw_chunk in normalized.split("+"):
            if not raw_chunk:
                continue
            chunk = alias_map.get(raw_chunk, raw_chunk)
            if chunk in MODIFIER_DISPLAY_ORDER:
                modifiers.add(chunk)
                continue
            if chunk.startswith("<keycode:") and chunk.endswith(">"):
                try:
                    primary_key = self.key_token_for_keycode(int(chunk[9:-1]))
                except ValueError:
                    pass
                continue
            if chunk.startswith("keycode"):
                try:
                    primary_key = self.key_token_for_keycode(int(chunk[7:]))
                except ValueError:
                    pass
                continue
            if chunk.startswith("f") and chunk[1:].isdigit():
                chunk = f"<{chunk}>"
            if chunk in PRIMARY_KEY_NAME_TO_KEYCODE:
                primary_key = self.key_token_for_keycode(PRIMARY_KEY_NAME_TO_KEYCODE[chunk])
        parts = [modifier for modifier in MODIFIER_DISPLAY_ORDER if modifier in modifiers]
        if primary_key is not None:
            parts.append(primary_key)
        return "+".join(parts)

    def hotkey_binding_parts(self, hotkey_text):
        normalized = self.normalize_hotkey(hotkey_text)
        modifiers = set()
        primary_key = None
        for part in normalized.split("+"):
            if not part:
                continue
            if self.is_modifier_key(part):
                modifiers.add(part)
            elif primary_key is None:
                primary_key = part
        return modifiers, primary_key

    def key_token_for_keycode(self, keycode):
        return f"<keycode:{int(keycode)}>"

    def keycode_from_token(self, key_token):
        if not key_token.startswith("<keycode:") or not key_token.endswith(">"):
            return None
        try:
            return int(key_token[9:-1])
        except ValueError:
            return None

    def display_name_for_keycode(self, keycode):
        label_map = {
            "return": "Return",
            "enter": "Enter",
            "tab": "Tab",
            "space": "Space",
            "backspace": "Backspace",
            "delete": "Delete",
            "esc": "Esc",
            "clear": "Clear",
            "left": "Left",
            "right": "Right",
            "up": "Up",
            "down": "Down",
        }
        mapped = MAC_KEYCODE_MAP.get(int(keycode))
        if mapped is None:
            return f"KeyCode{int(keycode)}"
        if mapped in label_map:
            return label_map[mapped]
        if mapped.startswith("<f") and mapped.endswith(">"):
            return mapped[1:-1].upper()
        return mapped.upper()

    def format_hotkey_display(self, hotkey_text):
        label_map = {
            "<cmd>": "Cmd",
            "<shift>": "Shift",
            "<ctrl>": "Ctrl",
            "<alt>": "Option",
        }
        display_parts = []
        modifiers, primary_key = self.hotkey_binding_parts(hotkey_text)
        for modifier in MODIFIER_DISPLAY_ORDER:
            if modifier in modifiers:
                display_parts.append(label_map[modifier])
        if primary_key is not None:
            keycode = self.keycode_from_token(primary_key)
            display_parts.append(self.display_name_for_keycode(keycode) if keycode is not None else primary_key.upper())
        return "+".join(display_parts)

    def is_modifier_key(self, key_name):
        return key_name in {"<cmd>", "<shift>", "<ctrl>", "<alt>"}

    def set_hotkey_var(self, target, value):
        display_value = self.format_hotkey_display(value)
        if target == "start_stop":
            self.start_stop_hotkey_var.set(display_value)
        elif target == "mute_hold":
            self.mute_hold_hotkey_var.set(display_value)

    def stop_hotkey_capture_monitor(self):
        if self.hotkey_capture_timeout_id is not None:
            try:
                self.root.after_cancel(self.hotkey_capture_timeout_id)
            except tk.TclError:
                pass
            self.hotkey_capture_timeout_id = None
        if self.hotkey_capture_monitor is not None:
            try:
                NSEvent.removeMonitor_(self.hotkey_capture_monitor)
            except Exception as exc:
                append_log(f"Failed to remove hotkey capture monitor: {exc}")
            self.hotkey_capture_monitor = None

    def reset_hotkey_capture_timeout(self):
        if self.hotkey_capture_timeout_id is not None:
            try:
                self.root.after_cancel(self.hotkey_capture_timeout_id)
            except tk.TclError:
                pass
        self.hotkey_capture_timeout_id = self.root.after(15000, self.on_hotkey_capture_timeout)

    def on_hotkey_capture_timeout(self):
        if not self.hotkey_capture_target:
            return
        self.cancel_hotkey_capture()
        self.set_status("Hotkey capture timed out. Click “Capture” and try again")

    def install_hotkey_capture_monitor(self):
        if self.hotkey_capture_monitor is None:
            mask = NSEventMaskFlagsChanged | NSEventMaskKeyDown
            self.hotkey_capture_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
                mask,
                self.local_hotkey_capture_event,
            )
        self.reset_hotkey_capture_timeout()

    def compose_hotkey_binding(self, modifiers, keycode):
        parts = [modifier for modifier in MODIFIER_DISPLAY_ORDER if modifier in modifiers]
        parts.append(self.key_token_for_keycode(keycode))
        return "+".join(parts)

    def update_capture_preview_from_parts(self, modifiers, keycode=None):
        display_parts = [modifier for modifier in MODIFIER_DISPLAY_ORDER if modifier in modifiers]
        if keycode is not None:
            display_parts.append(self.key_token_for_keycode(keycode))
        display_text = self.format_hotkey_display("+".join(display_parts))
        if display_text:
            self.set_status(f"Capturing hotkey: {display_text}")

    def local_hotkey_capture_event(self, event):
        if not self.hotkey_capture_target:
            return event
        event_type = int(event.type())
        flags = int(event.modifierFlags())
        keycode = int(event.keyCode())
        modifiers = self.modifier_names_from_flags(flags)
        self.hotkey_capture_modifiers = set(modifiers)
        self.reset_hotkey_capture_timeout()
        if event_type == NSEventTypeFlagsChanged:
            self.update_capture_preview_from_parts(modifiers)
            return event
        if event_type == NSEventTypeKeyDown:
            self.update_capture_preview_from_parts(modifiers, keycode)
            self.finish_hotkey_capture(modifiers=modifiers, keycode=keycode)
            return None
        return event

    def begin_hotkey_capture(self, target):
        if self.hotkey_capture_target == target:
            self.cancel_hotkey_capture()
            self.set_status("Canceled hotkey capture")
            return
        self.cancel_hotkey_capture()
        self.hotkey_capture_target = target
        self.hotkey_capture_modifiers.clear()
        self.hotkey_capture_keycode = None
        self.install_hotkey_capture_monitor()
        label = "Start / Stop" if target == "start_stop" else "Hold to Mute"
        self.set_status(f"Capturing {label} hotkey. Press the key combination. Click “Capture” again to cancel.")

    def finish_hotkey_capture(self, modifiers=None, keycode=None):
        if not self.hotkey_capture_target or keycode is None:
            return
        modifiers = set(modifiers or set())
        hotkey_value = self.compose_hotkey_binding(modifiers, keycode)
        target_name = self.hotkey_capture_target
        self.cancel_hotkey_capture()
        self.set_hotkey_var(target_name, hotkey_value)
        if not hasattr(self, "pending_hotkeys"):
            self.pending_hotkeys = {}
        self.pending_hotkeys["start_stop_hotkey" if target_name == "start_stop" else "mute_hold_hotkey"] = hotkey_value
        self.apply_settings()
        append_log(f"Hotkey captured: target={target_name} value={hotkey_value}")
        self.set_status(f"Hotkey updated to {self.format_hotkey_display(hotkey_value)}")

    def cancel_hotkey_capture(self):
        self.hotkey_capture_target = None
        self.hotkey_capture_modifiers.clear()
        self.hotkey_capture_keycode = None
        self.stop_hotkey_capture_monitor()

    def modifier_names_from_flags(self, flags):
        key_names = set()
        if flags & Quartz.kCGEventFlagMaskCommand:
            key_names.add("<cmd>")
        if flags & Quartz.kCGEventFlagMaskShift:
            key_names.add("<shift>")
        if flags & Quartz.kCGEventFlagMaskControl:
            key_names.add("<ctrl>")
        if flags & Quartz.kCGEventFlagMaskAlternate:
            key_names.add("<alt>")
        return key_names

    def carbon_modifiers_from_binding(self, binding):
        modifiers, primary_key = self.hotkey_binding_parts(binding)
        keycode = self.keycode_from_token(primary_key) if primary_key else None
        if keycode is None:
            return None, None
        carbon_modifiers = 0
        if "<cmd>" in modifiers:
            carbon_modifiers |= CARBON_CMD_KEY
        if "<shift>" in modifiers:
            carbon_modifiers |= CARBON_SHIFT_KEY
        if "<ctrl>" in modifiers:
            carbon_modifiers |= CARBON_CONTROL_KEY
        if "<alt>" in modifiers:
            carbon_modifiers |= CARBON_OPTION_KEY
        return int(keycode), int(carbon_modifiers)

    def install_carbon_hotkey_handler(self):
        if not CARBON_AVAILABLE:
            return False
        if self.carbon_hotkey_handler_ref is not None:
            return True

        def handler(_call_ref, event_ref, _user_data):
            if CARBON.GetEventClass(event_ref) != CARBON_KEYBOARD_EVENT_CLASS:
                return 0
            event_kind = int(CARBON.GetEventKind(event_ref))
            hotkey_id = CarbonEventHotKeyID()
            actual_size = ctypes.c_ulong(0)
            status = CARBON.GetEventParameter(
                event_ref,
                CARBON_EVENT_PARAM_DIRECT_OBJECT,
                CARBON_TYPE_EVENT_HOTKEY_ID,
                None,
                ctypes.sizeof(hotkey_id),
                ctypes.byref(actual_size),
                ctypes.byref(hotkey_id),
            )
            if status != 0:
                append_log(f"Failed to decode Carbon hotkey event: status={status}")
                return 0
            if hotkey_id.signature != CARBON_HOTKEY_SIGNATURE:
                return 0
            self.enqueue_ui_task(self.handle_registered_hotkey_event, int(hotkey_id.id), event_kind)
            return 0

        handler_ref = ctypes.c_void_p()
        event_types = (CarbonEventTypeSpec * 2)(
            CarbonEventTypeSpec(CARBON_KEYBOARD_EVENT_CLASS, CARBON_HOTKEY_PRESSED),
            CarbonEventTypeSpec(CARBON_KEYBOARD_EVENT_CLASS, CARBON_HOTKEY_RELEASED),
        )
        self.carbon_hotkey_target = CARBON.GetApplicationEventTarget()
        self.carbon_hotkey_handler_callback = CARBON_EVENT_HANDLER_CALLBACK(handler)
        status = CARBON.InstallEventHandler(
            self.carbon_hotkey_target,
            self.carbon_hotkey_handler_callback,
            len(event_types),
            event_types,
            None,
            ctypes.byref(handler_ref),
        )
        if status != 0:
            append_log(f"Failed to install Carbon hotkey handler: status={status}")
            self.carbon_hotkey_handler_callback = None
            self.carbon_hotkey_target = None
            return False
        self.carbon_hotkey_handler_ref = handler_ref
        append_log("Carbon hotkey handler installed")
        return True

    def unregister_carbon_hotkeys(self):
        for role, hotkey_ref in list(self.carbon_hotkey_refs.items()):
            try:
                status = CARBON.UnregisterEventHotKey(hotkey_ref) if CARBON is not None else 0
                if status != 0:
                    append_log(f"Failed to unregister Carbon hotkey ({role}): status={status}")
            except Exception as exc:
                append_log(f"Failed to unregister Carbon hotkey ({role}): {exc}")
        self.carbon_hotkey_refs.clear()
        self.carbon_hotkey_roles.clear()

    def remove_carbon_hotkey_handler(self):
        if self.carbon_hotkey_handler_ref is not None and CARBON is not None:
            try:
                status = CARBON.RemoveEventHandler(self.carbon_hotkey_handler_ref)
                if status != 0:
                    append_log(f"Failed to remove Carbon hotkey handler: status={status}")
            except Exception as exc:
                append_log(f"Failed to remove Carbon hotkey handler: {exc}")
        self.carbon_hotkey_handler_ref = None
        self.carbon_hotkey_handler_callback = None
        self.carbon_hotkey_target = None

    def register_carbon_hotkey(self, role, binding, hotkey_id):
        if not CARBON_AVAILABLE:
            return False
        keycode, modifiers = self.carbon_modifiers_from_binding(binding)
        if keycode is None:
            return False
        if not self.install_carbon_hotkey_handler():
            return False
        hotkey_ref = ctypes.c_void_p()
        status = CARBON.RegisterEventHotKey(
            keycode,
            modifiers,
            CarbonEventHotKeyID(CARBON_HOTKEY_SIGNATURE, hotkey_id),
            self.carbon_hotkey_target,
            0,
            ctypes.byref(hotkey_ref),
        )
        if status != 0:
            append_log(
                "Failed to register Carbon hotkey "
                f"({role}, binding={binding}, keycode={keycode}, modifiers=0x{modifiers:x}): status={status}"
            )
            return False
        self.carbon_hotkey_refs[role] = hotkey_ref
        self.carbon_hotkey_roles[int(hotkey_id)] = role
        return True

    def sync_carbon_hotkeys(self):
        if not CARBON_AVAILABLE:
            return
        self.unregister_carbon_hotkeys()
        settings = self.runtime.get_settings()
        registered_roles = []
        role_specs = (
            ("start_stop", settings.start_stop_hotkey, 1),
            ("mute_hold", settings.mute_hold_hotkey, 2),
        )
        for role, binding, hotkey_id in role_specs:
            if self.register_carbon_hotkey(role, binding, hotkey_id):
                registered_roles.append(role)
        if registered_roles:
            append_log(f"Carbon hotkeys registered ({', '.join(registered_roles)})")
        elif self.carbon_hotkey_handler_ref is not None:
            append_log("Carbon hotkey registration skipped for current bindings")

    def carbon_hotkey_registered(self, role):
        return role in self.carbon_hotkey_refs

    def handle_registered_hotkey_event(self, hotkey_id, event_kind):
        role = self.carbon_hotkey_roles.get(int(hotkey_id))
        if role is None:
            return
        settings = self.runtime.get_settings()
        if role == "start_stop":
            if event_kind == CARBON_HOTKEY_PRESSED and not self.suppress_status_reset:
                self.suppress_status_reset = True
                append_log(f"Global start/stop hotkey triggered (carbon): {settings.start_stop_hotkey}")
                self.toggle_monitoring_from_hotkey()
            elif event_kind == CARBON_HOTKEY_RELEASED:
                self.suppress_status_reset = False
            return
        if role == "mute_hold":
            if event_kind == CARBON_HOTKEY_PRESSED and not self.runtime.is_muted_until_release():
                self.runtime.set_muted_until_release(True)
                append_log(f"Global mute hotkey triggered (carbon): {settings.mute_hold_hotkey}")
                self.set_status("Global mute active. Release the hotkey to resume")
            elif event_kind == CARBON_HOTKEY_RELEASED and self.runtime.is_muted_until_release():
                self.runtime.set_muted_until_release(False)
                self.set_status("Global mute cleared")

    def update_hotkey_listener_state(self):
        sources = set()
        if self.carbon_hotkey_refs:
            sources.add("carbon")
        if self.hotkey_global_monitor is not None:
            sources.add("appkit-global")
        if self.hotkey_local_runtime_monitor is not None:
            sources.add("appkit-local")
        if self.hotkey_tap_source_name is not None:
            sources.add(self.hotkey_tap_source_name)
        self.hotkey_listener_sources = sources
        self.hotkey_listener_active = bool(sources)

    def describe_hotkey_listener_sources(self):
        label_map = {
            "carbon": "Carbon global hotkey",
            "appkit-global": "AppKit global monitor",
            "appkit-local": "AppKit local monitor",
            "session": "Session tap",
            "annotated": "Annotated tap",
            "hid": "HID tap",
        }
        if not self.hotkey_listener_sources:
            return "No listener attached"
        ordered = []
        for source in ("carbon", "appkit-global", "appkit-local", "session", "annotated", "hid"):
            if source in self.hotkey_listener_sources:
                ordered.append(label_map.get(source, source))
        return " + ".join(ordered)

    def install_appkit_hotkey_monitors(self):
        started_sources = []
        mask = NSEventMaskFlagsChanged | NSEventMaskKeyDown | NSEventMaskKeyUp
        if self.hotkey_global_monitor is None:
            self.hotkey_global_monitor_callback = self.handle_appkit_global_hotkey_event
            self.hotkey_global_monitor = NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
                mask,
                self.hotkey_global_monitor_callback,
            )
            if self.hotkey_global_monitor is not None:
                started_sources.append("appkit-global")
        if self.hotkey_local_runtime_monitor is None:
            self.hotkey_local_runtime_monitor_callback = self.handle_appkit_local_hotkey_event
            self.hotkey_local_runtime_monitor = NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
                mask,
                self.hotkey_local_runtime_monitor_callback,
            )
            if self.hotkey_local_runtime_monitor is not None:
                started_sources.append("appkit-local")
        self.update_hotkey_listener_state()
        if started_sources:
            append_log(f"AppKit hotkey monitors started ({', '.join(started_sources)})")
        return started_sources

    def handle_appkit_global_hotkey_event(self, event):
        self.dispatch_appkit_hotkey_event(event, "appkit-global")

    def handle_appkit_local_hotkey_event(self, event):
        self.dispatch_appkit_hotkey_event(event, "appkit-local")
        return event

    def dispatch_appkit_hotkey_event(self, event, source):
        event_type_map = {
            NSEventTypeFlagsChanged: Quartz.kCGEventFlagsChanged,
            NSEventTypeKeyDown: Quartz.kCGEventKeyDown,
            NSEventTypeKeyUp: Quartz.kCGEventKeyUp,
        }
        event_type = event_type_map.get(int(event.type()))
        if event_type is None:
            return
        self.dispatch_hotkey_event(
            event_type=event_type,
            flags=int(event.modifierFlags()),
            keycode=int(event.keyCode()),
            source=source,
        )

    def dispatch_hotkey_event(self, event_type, flags, keycode, source):
        event_signature = (
            int(event_type),
            tuple(sorted(self.modifier_names_from_flags(flags))),
            int(keycode),
        )
        now = time.monotonic()
        if (
            event_signature == self.last_hotkey_event_signature
            and now - self.last_hotkey_event_timestamp < 0.05
        ):
            return
        self.last_hotkey_event_signature = event_signature
        self.last_hotkey_event_timestamp = now
        if self.hotkey_event_counter < 8:
            append_log(
                "Global hotkey event received "
                f"({source}): type={event_type} keycode={keycode} flags=0x{flags:x}"
            )
        self.hotkey_event_counter += 1
        self.enqueue_ui_task(self.process_hotkey_event, int(event_type), int(flags), int(keycode))

    def hotkey_is_active(self, binding):
        required_modifiers, required_key = self.hotkey_binding_parts(binding)
        if required_key is None:
            return False
        return self.current_hotkey_modifiers == required_modifiers and required_key in self.current_hotkey_keys

    def handle_hotkey_press(self):
        settings = self.runtime.get_settings()

        if not self.carbon_hotkey_registered("mute_hold") and self.hotkey_is_active(settings.mute_hold_hotkey):
            if not self.runtime.is_muted_until_release():
                self.runtime.set_muted_until_release(True)
                append_log(f"Global mute hotkey triggered: {settings.mute_hold_hotkey}")
                self.set_status("Global mute active. Release the hotkey to resume")

        if not self.carbon_hotkey_registered("start_stop") and self.hotkey_is_active(settings.start_stop_hotkey):
            if not self.suppress_status_reset:
                self.suppress_status_reset = True
                append_log(f"Global start/stop hotkey triggered: {settings.start_stop_hotkey}")
                self.toggle_monitoring_from_hotkey()

    def handle_hotkey_release(self):
        settings = self.runtime.get_settings()
        if (
            not self.carbon_hotkey_registered("mute_hold")
            and self.runtime.is_muted_until_release()
            and not self.hotkey_is_active(settings.mute_hold_hotkey)
        ):
            self.runtime.set_muted_until_release(False)
            self.set_status("Global mute cleared")

        if (
            not self.carbon_hotkey_registered("start_stop")
            and self.suppress_status_reset
            and not self.hotkey_is_active(settings.start_stop_hotkey)
        ):
            self.suppress_status_reset = False

    def process_hotkey_event(self, event_type, flags, keycode):
        if self.hotkey_capture_target:
            return

        modifier_keys = self.modifier_names_from_flags(flags)
        key_token = self.key_token_for_keycode(keycode)
        self.current_hotkey_modifiers = set(modifier_keys)

        if event_type == Quartz.kCGEventFlagsChanged:
            self.current_hotkey_keys.clear()
            self.handle_hotkey_release()
            return

        if event_type == Quartz.kCGEventKeyDown:
            self.current_hotkey_keys = {key_token}
            self.handle_hotkey_press()
            return

        if event_type == Quartz.kCGEventKeyUp:
            self.current_hotkey_keys.discard(key_token)
            self.handle_hotkey_release()

    def hotkey_event_callback(self, _proxy, event_type, event, _refcon):
        disabled_by_user_input = getattr(Quartz, "kCGEventTapDisabledByUserInput", None)
        if event_type in (Quartz.kCGEventTapDisabledByTimeout, disabled_by_user_input) and self.hotkey_event_tap is not None:
            Quartz.CGEventTapEnable(self.hotkey_event_tap, True)
            return event

        if event_type not in (Quartz.kCGEventKeyDown, Quartz.kCGEventKeyUp, Quartz.kCGEventFlagsChanged):
            return event

        flags = int(Quartz.CGEventGetFlags(event))
        keycode = int(Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode))
        self.dispatch_hotkey_event(event_type, flags, keycode, self.hotkey_tap_source_name or "tap")
        return event

    def start_hotkey_listener(self, force=False):
        try:
            listener_thread_alive = self.hotkey_thread is not None and self.hotkey_thread.is_alive()
            if not force and (self.hotkey_listener_active or listener_thread_alive):
                return
            self.last_hotkey_attach_attempt = time.time()
            permission_granted = has_accessibility_permission()
            if not permission_granted:
                append_log("Global hotkey permission reported unavailable; trying event tap attach anyway")
            self.sync_carbon_hotkeys()
            self.update_hotkey_listener_state()
            self.install_appkit_hotkey_monitors()
            if self.hotkey_thread is not None and self.hotkey_thread.is_alive():
                return

            def run_event_tap():
                mask = (
                    (1 << Quartz.kCGEventKeyDown)
                    | (1 << Quartz.kCGEventKeyUp)
                    | (1 << Quartz.kCGEventFlagsChanged)
                )
                self.hotkey_event_tap_callback = self.hotkey_event_callback
                tap = None
                tap_name = None
                for tap_location, location_name in (
                    (Quartz.kCGSessionEventTap, "session"),
                    (Quartz.kCGAnnotatedSessionEventTap, "annotated"),
                    (Quartz.kCGHIDEventTap, "hid"),
                ):
                    tap = Quartz.CGEventTapCreate(
                        tap_location,
                        Quartz.kCGHeadInsertEventTap,
                        Quartz.kCGEventTapOptionListenOnly,
                        mask,
                        self.hotkey_event_tap_callback,
                        None,
                    )
                    if tap is not None:
                        tap_name = location_name
                        break
                if tap is None:
                    append_log(f"Global hotkey event tap failed to start (permission={permission_granted})")
                    self.hotkey_event_tap = None
                    self.hotkey_run_loop = None
                    self.hotkey_tap_source_name = None
                    self.update_hotkey_listener_state()
                    if permission_granted:
                        self.enqueue_ui_task(self.set_status, "Global hotkey listener attach failed. Click “Retry Listener Attach” or restart the app")
                    return

                run_loop = Quartz.CFRunLoopGetCurrent()
                source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
                self.hotkey_event_tap = tap
                self.hotkey_run_loop = run_loop
                self.hotkey_tap_source_name = tap_name
                self.hotkey_event_counter = 0
                self.last_hotkey_event_signature = None
                self.last_hotkey_event_timestamp = 0.0
                self.update_hotkey_listener_state()
                Quartz.CFRunLoopAddSource(run_loop, source, Quartz.kCFRunLoopCommonModes)
                Quartz.CGEventTapEnable(tap, True)
                append_log(f"Global hotkey event tap started ({tap_name})")
                Quartz.CFRunLoopRun()
                append_log(f"Global hotkey event tap stopped ({tap_name})")
                self.hotkey_event_tap = None
                self.hotkey_run_loop = None
                self.hotkey_tap_source_name = None
                self.update_hotkey_listener_state()

            self.hotkey_thread = threading.Thread(target=run_event_tap, daemon=True)
            self.hotkey_thread.start()
        except Exception as exc:
            append_log(f"Global hotkey listener failed: {exc}")
            self.set_status("Global hotkey startup failed. Check Accessibility permission")

    def stop_hotkey_listener(self):
        self.unregister_carbon_hotkeys()
        self.remove_carbon_hotkey_handler()
        if self.hotkey_global_monitor is not None:
            try:
                NSEvent.removeMonitor_(self.hotkey_global_monitor)
            except Exception as exc:
                append_log(f"Failed to remove AppKit global hotkey monitor: {exc}")
        if self.hotkey_local_runtime_monitor is not None:
            try:
                NSEvent.removeMonitor_(self.hotkey_local_runtime_monitor)
            except Exception as exc:
                append_log(f"Failed to remove AppKit local hotkey monitor: {exc}")
        self.hotkey_global_monitor = None
        self.hotkey_global_monitor_callback = None
        self.hotkey_local_runtime_monitor = None
        self.hotkey_local_runtime_monitor_callback = None
        if self.hotkey_event_tap is not None:
            try:
                Quartz.CFMachPortInvalidate(self.hotkey_event_tap)
            except Exception:
                pass
        if self.hotkey_run_loop is not None:
            try:
                Quartz.CFRunLoopStop(self.hotkey_run_loop)
            except Exception:
                pass
        self.hotkey_event_tap = None
        self.hotkey_run_loop = None
        self.hotkey_thread = None
        self.hotkey_tap_source_name = None
        self.hotkey_event_counter = 0
        self.last_hotkey_event_signature = None
        self.last_hotkey_event_timestamp = 0.0
        self.current_hotkey_modifiers.clear()
        self.current_hotkey_keys.clear()
        self.suppress_status_reset = False
        self.update_hotkey_listener_state()

    def restart_hotkey_listener(self, force=True):
        self.stop_hotkey_listener()
        self.start_hotkey_listener(force=force)

    def toggle_monitoring_from_hotkey(self):
        if self.runtime.running:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def refresh_preview(self):
        self.ui.update_preview(self.runtime.get_latest_preview())
        self.update_runtime_chips()
        self.root.after(80, self.refresh_preview)

    def reset_defaults(self):
        settings, defaults = self.runtime.get_settings(), GuardSettings()
        preserved = {"blacklist_apps", "start_stop_hotkey", "mute_hold_hotkey", "launch_at_login",
                     "language", "preview_enabled", "alert_sound_enabled"}
        for name in defaults.__dataclass_fields__:
            if name not in preserved:
                setattr(settings, name, getattr(defaults, name))
        self.runtime.update_settings(settings)
        save_settings(settings)
        self.populate_form_from_settings(settings)
        self.set_status("Defaults restored")

    def populate_form_from_settings(self, settings):
        values = {
            "max_allowed_people": settings.max_allowed_people,
            "cooldown_seconds": settings.cooldown_seconds,
            "camera_index": settings.camera_index,
            "trigger_frame_threshold": settings.trigger_frame_threshold,
            "frame_scale": settings.frame_scale,
            "confidence_threshold": settings.confidence_threshold,
            "detect_imgsz": settings.detect_imgsz,
            "self_box_expand_x": settings.self_box_expand_x,
            "self_box_expand_y_top": settings.self_box_expand_y_top,
            "self_box_expand_y_bottom": settings.self_box_expand_y_bottom,
            "self_track_max_misses": settings.self_track_max_misses,
            "self_track_min_confidence": settings.self_track_min_confidence,
            "min_risk_box_area_ratio": settings.min_risk_box_area_ratio,
            "far_target_confidence": settings.far_target_confidence,
        }

        for key, value in values.items():
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, str(value))

        self.preview_var.set(settings.preview_enabled)
        self.alert_sound_var.set(settings.alert_sound_enabled)
        self.far_target_boost_var.set(settings.far_target_boost_enabled)
        self.model_var.set(settings.model_name)
        self.backend_var.set(settings.inference_backend)
        self.start_stop_hotkey_var.set(self.format_hotkey_display(settings.start_stop_hotkey))
        self.mute_hold_hotkey_var.set(self.format_hotkey_display(settings.mute_hold_hotkey))
        self.launch_at_login_var.set(settings.launch_at_login)
        self.blacklist_text.delete("1.0", "end")
        self.blacklist_text.insert("1.0", "\n".join(settings.blacklist_apps))
        self.refresh_form_summaries()

    def quit_application(self):
        stack_preview = "".join(traceback.format_stack(limit=6))
        append_log("quit_application invoked\n" + stack_preview)
        self.ui_task_polling = False
        self.cancel_hotkey_capture()
        if self.runtime.running:
            self.runtime.stop_event.set()
            if self.runtime.thread is not None:
                self.runtime.thread.join(timeout=1.5)
        self.stop_hotkey_listener()
        self.root.destroy()


def main():
    # Offline diagnostic also exercises the frozen app's native libraries.
    # It creates no window, hotkey listener, camera capture, or app-hide worker.
    if len(sys.argv) > 1 and sys.argv[1] == "--check-inference":
        import argparse
        parser = argparse.ArgumentParser(description="Check local inference using an image; no camera or app actions")
        parser.add_argument("image", type=Path)
        parser.add_argument("--backend", choices=("auto", "coreml", "pytorch"), default="auto")
        parser.add_argument("--model", default="yolo26s.pt")
        parser.add_argument("--imgsz", type=int, default=1280)
        parser.add_argument("--report", type=Path, required=True)
        args = parser.parse_args(sys.argv[2:])
        frame = cv2.imread(str(args.image))
        if frame is None:
            parser.error("Image is not readable")
        detector = create_detector(resolve_model_path(args.model), args.backend, args.imgsz,
                                   (RESOURCE_DIR / ".models", RESOURCE_DIR / "models", APP_SUPPORT_DIR / "models"))
        detections = detector.detect(frame, 0.30, args.imgsz)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps({"model": args.model, "backend": detector.description, "notice": detector.notice,
                                          "detections": detections}, indent=2) + "\n", encoding="utf-8")
        return
    append_log("Application starting")
    try:
        root = tk.Tk()
        app = ChillGuardApp(root)
        if sys.platform == "darwin":
            try:
                root.createcommand("tk::mac::Quit", app.quit_application)
                append_log("Registered tk::mac::Quit handler")
            except Exception as exc:
                append_log(f"Failed to register tk::mac::Quit handler: {exc}")
        append_log("Entering Tk mainloop")
        root.mainloop()
        append_log("Tk mainloop exited")
    except Exception:
        append_log("Unhandled startup error:\n" + traceback.format_exc())
        raise


if __name__ == "__main__":
    main()

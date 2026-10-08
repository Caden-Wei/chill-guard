"""Presentation-only localization; model names, keycodes and logs keep their identity."""
import re


TEXT = {
    "Hide selected apps when your protection rules trigger.": "保护规则触发时，隐藏你指定的应用。",
    "Detection configuration": "检测配置", "Quick controls": "快速控制",
    "Toggle protection with your global shortcut.": "使用全局快捷键切换保护状态。",
    "Change shortcut…": "更改快捷键…", "Hide preview": "隐藏预览",
    "Use the exact process name. Changes take effect after Save changes.": "使用准确的进程名称，点击「保存更改」后生效。",
    "Add process name": "添加进程名称", "Exact process name": "准确的进程名称",
    "Analyze the camera view locally after starting.": "开始保护后，在本机分析摄像头画面。",
    "Detection continues while the preview is hidden.": "隐藏预览时，检测仍会继续。",
    "Protection is active": "正在保护", "Preparing camera": "正在准备摄像头",
    "Alerts paused": "提醒已暂停", "Check status below": "请查看下方状态",
    "Hiding apps": "正在隐藏应用", "Protection has not started": "尚未开始保护",
    "Starting": "启动中", "Manage all applications": "管理全部应用",
    "Overview": "监测概览", "Protected apps": "保护应用", "Detection": "检测设置",
    "Shortcuts & startup": "快捷键与启动", "Language": "语言", "Local privacy protection": "本地隐私保护",
    "Shortcuts": "快捷键与启动", "File": "文件", "Edit": "编辑", "Window": "窗口", "Help": "帮助",
    "Cut": "剪切", "Copy": "复制", "Paste": "粘贴", "Select all": "全选", "Switch language": "切换语言", "About Chill Guard": "关于 Chill Guard",
    "Your private workspace": "守护你的私人空间", "Start protection": "开始保护", "Stop protection": "停止保护",
    "Ready when you are": "准备就绪", "Monitoring is active": "正在保护", "Protection needs attention": "保护需要处理",
    "Alerts are temporarily muted": "提醒已临时静音", "Protection triggered": "已触发保护",
    "Camera preview": "摄像头预览", "Show preview": "显示预览", "Camera is off": "摄像头尚未开启",
    "Start protection to analyze the scene locally.\nYour camera images stay on this Mac.": "开始保护后，在本机分析摄像头画面。\n摄像头图像保留在这台 Mac 上。",
    "Preview is hidden": "预览已隐藏",
    "Detection continues while the preview is hidden.\nEnable Show preview to inspect the camera view.": "隐藏预览时，检测仍会继续。\n开启「显示预览」可查看摄像头画面。",
    "Preparing the camera…": "正在准备摄像头…", "Waiting for the first frame.": "正在等待第一帧画面。",
    "People": "有效人数", "Allowed": "允许人数", "Standby": "待机", "Running": "运行中", "Monitoring": "检测中",
    "Muted": "静音", "Error": "错误", "Alert": "保护触发", "Alerting": "正在保护",
    "Detection model": "检测模型", "Inference engine": "推理引擎", "Configured engine": "已配置引擎",
    "Protected applications": "保护应用", "Start / stop shortcut": "开始 / 停止快捷键", "Not loaded yet": "尚未加载",
    "Apple Core ML (recommended)": "Apple Core ML（推荐）", "Automatic": "自动选择", "PyTorch compatibility": "PyTorch 兼容模式",
    "YOLO26s (recommended)": "YOLO26s（推荐）", "YOLO11s (legacy)": "YOLO11s（旧版）", "YOLO11n (lightweight)": "YOLO11n（轻量）",
    "Model and engine": "模型与推理", "Protection rules": "保护规则", "Camera": "摄像头", "Feedback": "反馈",
    "Basic": "基础设置", "Advanced": "高级设置", "Back to Basics": "返回基础设置",
    "Tune detection for your workspace.": "为你的使用环境调整检测。",
    "Native exports are bundled at 1280. Other sizes use the compatibility engine.": "随应用提供 1280 尺寸的原生模型。其他尺寸使用兼容引擎。",
    "Allowed people (including you)": "允许人数（包含你）", "Consecutive trigger frames": "连续触发帧数",
    "Alert cooldown (seconds)": "保护冷却时间（秒）", "Confidence threshold": "置信度阈值",
    "Camera index": "摄像头编号", "Frame scale": "画面缩放比例", "Detection size": "检测尺寸",
    "Play alert sound": "播放提醒声音", "Test sound": "测试声音", "Ignore-zone geometry": "忽略区域范围",
    "Horizontal expansion": "横向扩展比例", "Top expansion": "顶部扩展比例", "Bottom expansion": "底部扩展比例",
    "Main-user tracking": "主用户跟踪", "Tracking confidence": "跟踪置信度", "Missed-frame tolerance": "丢失帧容差",
    "Minimum risk-box area ratio": "风险目标最小面积比例", "Long-range boost": "远距离增强",
    "Enable long-range boost": "启用远距离增强", "Boost confidence": "增强置信度",
    "Main-user tracking uses geometry, not facial identity. Review these rules in your actual camera scene.": "主用户跟踪基于位置与大小，不识别人脸身份。请结合实际摄像头场景检查这些规则。",
    "Apps on this list are hidden when your protection rules trigger.": "保护规则触发时，隐藏列表中的应用。",
    "Application names": "应用名称", "One exact process name per line. Changes take effect after Save changes.": "每行填写一个准确的进程名称。点击「保存更改」后生效。",
    "Add application…": "添加应用…", "Choose an application": "选择应用", "Applications": "应用程序",
    "No applications listed": "还没有添加应用", "Add at least one application before starting protection.": "开始保护前，请至少添加一个应用。",
    "Keep protection within reach.": "随时控制保护状态。", "Global shortcuts": "全局快捷键",
    "Start / stop": "开始 / 停止", "Hold to mute": "按住静音", "Capture": "录制",
    "Press Capture, then your key combination. Hold the mute shortcut to suppress alerts until release.": "点击「录制」后按下组合键。按住静音快捷键可暂停提醒，松开后恢复。",
    "Retry listener": "重试监听", "Accessibility settings": "辅助功能设置", "Startup": "启动",
    "Launch at login": "登录时启动", "Changes to startup take effect immediately.": "启动选项的更改立即生效。",
    "Save changes": "保存更改", "Saved": "已保存", "Unsaved changes": "有未保存的更改",
    "Restore detection defaults": "恢复检测默认值", "Restore detection settings?": "恢复检测设置？",
    "This resets detection parameters. Your application list, shortcuts, language and startup choice are kept.": "将重置检测参数。应用列表、快捷键、语言和启动选项会保留。",
    "Local processing · No image upload": "本机处理 · 图像不上传", "Show Main Window": "显示主窗口",
    "Start Monitoring": "开始保护", "Stop Monitoring": "停止保护", "Quit": "退出",
    "Invalid Settings": "设置无效", "Launch-at-login update failed": "更新登录启动设置失败",
    "Some parameters are invalid. Check the numeric fields.": "部分参数无效，请检查数字输入。",
    "Frame scale should be between 0.1 and 1.0.": "画面缩放比例须为 0.1 至 1.0。",
    "Confidence threshold should be between 0.05 and 1.0.": "置信度阈值须为 0.05 至 1.0。",
    "Detect size should be between 320 and 1600.": "检测尺寸须为 320 至 1600。",
    "Long-range boost threshold should be between 0.05 and 1.0.": "远距离增强阈值须为 0.05 至 1.0。",
    "Trigger frames must be at least 1.": "连续触发帧数须至少为 1。", "Camera index cannot be negative.": "摄像头编号不能为负数。",
    "Allowed people must be at least 1, including the main user.": "允许人数须至少为 1，包含主用户。",
    "Choose auto, coreml, or pytorch inference.": "请选择有效的推理引擎。",
    "Blacklist cannot be empty. Keep at least one app name.": "保护应用列表不能为空，请至少保留一个应用。",
    "Start/stop hotkey cannot be empty.": "开始 / 停止快捷键不能为空。", "Hold-to-mute hotkey cannot be empty.": "按住静音快捷键不能为空。",
    "Cooldown cannot be negative.": "保护冷却时间不能为负数。", "Ignore-zone expansions cannot be negative.": "忽略区域扩展比例不能为负数。",
    "Tracking confidence should be between 0.05 and 1.0.": "跟踪置信度须为 0.05 至 1.0。",
    "Missed-frame tolerance cannot be negative.": "丢失帧容差不能为负数。", "Risk-box area ratio should be between 0 and 1.": "风险目标面积比例须为 0 至 1。",
    "Settings applied": "设置已保存", "Defaults restored": "检测默认值已恢复", "Loading model...": "正在加载模型…",
    "Alert action executed": "已执行应用隐藏操作", "Check Automation permission": "请检查自动化权限",
    "Test app hide executed": "已执行应用隐藏测试",
    "Temporary mute test enabled. It will auto-clear in 5 seconds": "已临时静音，5 秒后自动解除",
    "Temporary mute test cleared": "临时静音测试已解除",
    "Starting monitoring...": "正在启动保护…", "Stopping monitoring...": "正在停止保护…",
    "Monitoring is already running": "保护已在运行", "Monitoring is not running": "保护尚未运行",
    "Preview enabled": "预览已开启", "Preview disabled": "预览已关闭", "Alert sound enabled": "提醒声音已开启", "Alert sound disabled": "提醒声音已关闭",
    "Launch-at-login setting updated": "登录启动设置已更新", "Played the test alert sound": "已播放测试声音",
    "Retried global hotkey listener attach": "已重新连接全局快捷键监听",
    "Retried listener attach. If it still fails, confirm Accessibility is enabled for this app": "已重试监听。若仍无法使用，请确认辅助功能权限。",
    "Opened Accessibility settings. Enable Chill Guard there": "已打开辅助功能设置，请启用 Chill Guard",
    "Opened Accessibility settings. Enable Python or Terminal there": "已打开辅助功能设置，请启用 Python 或终端",
    "Main window hidden. Reopen it from the menu bar icon": "主窗口已隐藏，可从 Dock 菜单重新打开",
    "Global mute active. Release the hotkey to resume": "正在按住静音，松开快捷键后恢复", "Global mute cleared": "全局静音已解除",
    "Canceled hotkey capture": "已取消快捷键录制", "Hotkey capture timed out. Click “Capture” and try again": "录制超时，请点击「录制」重试",
    "Global hotkey startup failed. Check Accessibility permission": "全局快捷键启动失败，请检查辅助功能权限",
    "The listener is attached, but macOS still does not consider this app authorized": "监听已连接，但 macOS 尚未确认本应用的辅助功能权限",
    "Accessibility is authorized. Retrying global listener attach": "辅助功能已授权，正在重连全局监听",
    "Global hotkeys unavailable: grant Accessibility permission to Chill Guard.app": "全局快捷键不可用，请授予 Chill Guard 辅助功能权限",
    "Global hotkeys unavailable: source mode requires Accessibility permission for the current Python": "源码模式需要为当前 Python 授予辅助功能权限",
    "This test bundle is in a temporary directory and does not have Accessibility permission yet": "临时测试应用尚未获得辅助功能权限",
    "This test bundle is in a temporary directory and needs its own Accessibility permission": "临时测试应用需要单独授予辅助功能权限",
    "Cannot open the camera. Check permissions, the selected index, or whether another app is using it.": "无法打开摄像头。请检查权限、摄像头编号，或是否被其他应用占用。",
    "Failed to read a camera frame. Check the device connection state.": "无法读取摄像头画面，请检查设备连接。",
    "Monitoring stopped": "保护已停止", "Camera and model are active and analyzing the scene.": "摄像头与模型正在分析画面。",
    "Ready. Start monitoring when you are set.": "准备就绪，可以开始保护。",
}


class Language:
    def __init__(self, code="zh"):
        self.code = code if code in ("zh", "en") else "zh"

    def text(self, message, **values):
        return (TEXT.get(message, message) if self.code == "zh" else message).format(**values)

    def system(self, message):
        """Translate feedback at the display boundary; preserve technical diagnostics."""
        if self.code == "en":
            return message
        if message in TEXT:
            return TEXT[message]
        patterns = [
            (r"People (.+)", "有效人数 {}"), (r"Allowed (.+)", "允许人数 {}"),
            (r"Hotkey updated to (.+)", "快捷键已更新为 {}"), (r"Capturing hotkey: (.+)", "正在录制：{}"),
            (r"Capturing (.+) hotkey\. Press the key combination\. Click “Capture” again to cancel\.", "正在录制 {} 快捷键，请按下组合键。再次点击「录制」可取消。"),
            (r"Global hotkeys enabled \((.+)\)", "全局快捷键已连接（{}）"),
            (r"Current authorized target: (.+)", "当前授权目标：{}"),
            (r"Re-enable this exact path in Accessibility: (.+)", "请在辅助功能中重新启用此路径：{}"),
            (r"Confirm Accessibility is enabled for this app: (.+)", "请确认此应用已启用辅助功能权限：{}"),
            (r"Confirm the temporary test app is checked: (.+)", "请确认已勾选此临时应用：{}"),
            (r"Confirm the checked app is this one: (.+)", "请确认已勾选的应用路径：{}"),
            (r"Enable this target in Accessibility: (.+)", "请在辅助功能中启用：{}"),
            (r"Model ready: (.+)", "模型就绪：{}"), (r"Monitoring: (.+)", "实际推理：{}"), (r"Monitoring stopped: (.+)", "保护已停止：{}"),
            (r"Alert failed: (.+)", "保护操作失败：{}"), (r"Failed to read a camera frame: (.+)", "摄像头读取失败：{}"),
            (r"Test app hide failed: (.+)", "应用隐藏测试失败：{}"),
            (r"Muted: detected (\d+) risk targets", "已静音：检测到 {} 个风险目标"),
            (r"Alert triggered.*", "风险条件已满足，正在隐藏保护应用。"),
            (r"Alert already in progress.*", "正在执行保护操作。"),
        ]
        for pattern, translated in patterns:
            match = re.fullmatch(pattern, message)
            if match:
                groups = tuple(self.system(value) for value in match.groups())
                if pattern.startswith("Capturing ("):
                    groups = tuple({"Start / Stop": "开始 / 停止", "Hold to Mute": "按住静音"}.get(v, v) for v in groups)
                return translated.format(*groups)
        # Backend names are technical identities; translate their explanatory text.
        message = message.replace("CPU + Neural Engine", "CPU + 神经网络引擎")
        message = re.sub(r" / camera (\d+)( connected)?", r" / 摄像头 \1", message)
        message = message.replace("Core ML export is missing for this detection size. Using PyTorch.", "此检测尺寸没有原生模型，已回退到 PyTorch。")
        message = message.replace("Core ML unavailable:", "Core ML 不可用：").replace("Core ML inference failed:", "Core ML 推理失败：").replace("Using PyTorch.", "已回退到 PyTorch。")
        return message

# Chill Guard 安装指南

[English](INSTALL.md)

## 适用平台

- 当前版本支持 `macOS`

## macOS 安装方式

你会拿到：

- `Chill Guard-macOS.dmg`

推荐安装方式：

1. 双击打开 `Chill Guard-macOS.dmg`
2. 将 `Chill Guard.app` 拖到 `Applications`
3. 从“应用程序”里启动 `Chill Guard`

## 第一次启动要做什么

第一次用时，先确认这两个权限：

1. 摄像头权限
2. 辅助功能权限

辅助功能权限主要用来：

- 接收全局快捷键
- 在触发风险时切换或隐藏你配置的软件

如果全局快捷键没反应，先去：

- `系统设置 -> 隐私与安全性 -> 辅助功能`

确认你勾选的是当前正在运行的这份 `Chill Guard.app`。

## 基本使用流程

1. 打开 `Chill Guard`
2. 在 `Detection` 里确认摄像头和检测参数
3. 在 `Hotkeys` 里录制 `Start / Stop` 和 `Hold to Mute`
4. 在黑名单里填你想藏起来的软件名
5. 点击 `Apply Settings`
6. 点击 `Start Monitoring`

## 主要功能

- `Start / Stop hotkey`：快速开始或停止监测
- `Hold to Mute hotkey`：按住时临时静默，松开恢复
- `Preview`：显示当前摄像头画面
- `Alert Sound`：风险触发时播放提示音
- `Apps to Hide`：检测到风险后要切换或隐藏的软件列表

## 推理后端

Detection 里的 `Inference` 提供 `pytorch`（默认）、`coreml` 和 `auto`。
Core ML 需要与模型、输入尺寸匹配的导出文件和运行依赖；构建者按 [Apple 本地推理说明](APPLE_INFERENCE.md) 准备后，安装包会包含这些文件。`auto` 优先使用匹配的原生模型，否则使用 PyTorch。选择 `coreml` 后，如果导出文件缺失或运行失败，也会回退到 PyTorch，状态和日志会说明原因及实际后端。监测中修改 Model File、Inference 或 Detect Size，会重新加载检测器。

Model File 仍填写原始 `.pt` 文件，例如 `yolo11s.pt`。程序按权重校验值和检测尺寸匹配原生导出文件。使用 640 导出时，远距离增强会请求 1280 输入并回退到 PyTorch；准备默认的 1280 导出，才能让两次检测都使用 Core ML。

连续触发帧数、模型和推理后端等设置会在重启后保留。按住静默键时，声音和隐藏动作都暂停，检测继续运行。预览通过留边显示完整摄像头画面，保留边缘目标。

## 常见问题

### 1. 全局快捷键没反应

先检查：

- 你是不是开的是安装后的那一份 app，而不是别的旧副本
- 辅助功能里勾选的是不是这份 app
- 有没有把快捷键设成鼠标驱动自己模拟的特殊功能键

### 2. 摄像头打不开

先检查：

- 系统有没有给 `Chill Guard` 摄像头权限
- 有没有别的软件已经独占摄像头

### 3. 检测到人以后没有切换软件

先检查：

- 黑名单里的软件名是不是填对了
- 辅助功能权限是不是已经打开

## 分发建议

给其他 mac 用户时，建议发这两个文件：

- `Chill Guard-macOS.dmg`
- 这份安装指南

如果对方第一次打开时看到系统安全提示：

- 右键 `Chill Guard.app`
- 选择“打开”
- 再确认一次

这属于本地构建、未公证应用的正常现象。

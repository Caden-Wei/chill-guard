# Chill Guard

[English](README.md)

Chill Guard 是一个给上班摸鱼用的 macOS 小工具。它会看本地摄像头画面，判断当前有多少人出现在你旁边；如果人数超过你设定的上限，就自动把你指定的软件藏起来。

当前状态：

- 仅支持 `macOS`
- 本地桌面应用，不是云服务
- 基于 `tkinter`、`OpenCV`、`PyObjC`、`ultralytics` 和 `PyInstaller`
- 1.2.1 版修复相机预览中的加载层闪烁，以及隐藏预览后的旧画面残留。见 [预览修复验证](validation/PREVIEW_FLICKER_2026-10-10.md)。

## 主要功能

- 实时监测内置或外接摄像头
- 将其中一人视为主用户，统计额外进入画面的人数
- 当可见人数超过配置上限时触发隐藏流程
- 播放本地提示音
- 通过 macOS 辅助功能自动隐藏指定应用
- 支持全局开始/停止和按住静默快捷键
- 支持登录时自动启动

## 不做什么

- 不进行身份识别
- 不会把摄像头画面上传到远端
- 当前不支持 Windows

## 工作原理

应用使用 YOLO 人体检测模型，只检测 `person` 这一类目标。先去掉重复框，再选取主用户；其余目标经过自身排除、缓冲区和最小面积规则筛选。界面人数与触发判断使用同一组有效目标，人数包括当前可见的主用户。超过人数上限并达到配置的连续帧数时，Chill Guard 会播放提醒，并尝试隐藏指定应用。

1.2 版默认使用 YOLO26s 与 Apple Core ML，检测尺寸为 1280，提供已导出的本地模型。允许 CPU 和 Neural Engine 执行，具体分配由系统决定；失败时显示原因并回退到 PyTorch。读取设置时保留明确的旧模型选择，本次经用户授权的本地升级切换到 YOLO26s。界面新增概览、保护应用、检测设置、快捷键与启动四页，中英文可即时切换，覆盖反馈和 Dock 菜单。配置与验证方法见 [Apple 本地推理说明](docs/APPLE_INFERENCE.md)。

## 仓库结构

- `chill_guard_app.py`：主程序
- `person_detector.py`：Core ML/PyTorch 本地推理与原生后端失败回退
- `chill_guard_ui.py` 与 `chill_guard_i18n.py`：桌面界面与中英文展示
- `tools/export_coreml.py`：准备固定尺寸的 YOLO11/YOLO26 FP16 Core ML 模型
- `tools/benchmark_inference.py`：用本地图片对比推理，不调用摄像头
- `Chill Guard.spec`：macOS 打包用的 PyInstaller 配置
- `packaging/build_macos_release.sh`：macOS 发布脚本
- `docs/INSTALL.md`：英文安装指南
- `docs/INSTALL.zh-CN.md`：中文安装指南
- `yolo26s.pt`：打包默认模型文件
- `yolo11s.pt`：旧版可选模型
- `yolo11n.pt`：更轻量的可选模型

## 运行要求

- `macOS`
- Python `3.12`
- 摄像头权限
- 辅助功能权限
- 按 `requirements.txt` 安装好的本地 Python 环境

## 从源码运行

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt -r requirements-coreml.txt
python tools/export_coreml.py --model yolo26s.pt --imgsz 1280
python chill_guard_app.py
```

如果本机缺少 `tkinter`，需要先安装 Homebrew 的 Python/Tk 组合。

## 打包 macOS 应用

```bash
./packaging/build_macos_release.sh
```

脚本会在 `dist/` 里生成 DMG。

## 所需权限

Chill Guard 需要：

- 摄像头权限：用于读取本地摄像头画面
- 辅助功能权限：用于接收全局快捷键并隐藏指定应用
- Apple Events 自动化权限：用于隐藏指定应用和管理登录项

## 开源与许可证

本仓库使用 `AGPL-3.0-or-later` 许可证。

原因很直接：项目当前依赖 `ultralytics`，其官方许可证模型为 AGPL-3.0 或商业企业授权。如果你计划把这份代码用于闭源产品，需要先核对上游许可证要求。

参考：

- [Ultralytics licensing overview](https://docs.ultralytics.com/license/)
- [GNU AGPL v3](https://www.gnu.org/licenses/agpl-3.0.txt)

## 已知限制

- 应用通过 `PyObjC` 强绑定 macOS 系统 API
- 全局快捷键依赖 macOS 输入链路和辅助功能行为
- 隐藏第三方应用依赖 AppleScript/System Events，不同目标应用表现可能不同
- 人数统计基于启发式规则，受机位、光线和重复检测影响

## 开发说明

- 不要提交 `dist/`、`build/`、`.venv/` 或运行日志
- 可以用下面命令做语法检查：

```bash
python -m py_compile chill_guard_app.py
python -m unittest discover -s tests -v
```

- 涉及用户可见行为改动时，同时更新 `docs/INSTALL.md` 和 `docs/INSTALL.zh-CN.md`

本次界面按[五个生图方向及评估](design/concepts/EVALUATION.md)实施，用户授权自行选择第 01 个 macOS Air 方向，再还原为实际的圆角控件、应用行和可滚动表单。[验证记录](validation/DESKTOP_AIR_2026-10-08.md)区分推理、设置保留、视觉检查与实际权限限制。

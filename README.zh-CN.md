# Chill Guard

[English](README.md)

Chill Guard 是一个给上班摸鱼用的 macOS 小工具。它会看本地摄像头画面，判断当前有多少人出现在你旁边；如果人数超过你设定的上限，就自动把你指定的软件藏起来。

当前状态：

- 仅支持 `macOS`
- 本地桌面应用，不是云服务
- 基于 `tkinter`、`OpenCV`、`PyObjC`、`ultralytics` 和 `PyInstaller`

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

应用使用 YOLO 人体检测模型，只检测 `person` 这一类目标。随后用启发式规则选出“主用户”框，并统计画面里剩余人数。当 `visible_people > max_allowed_people` 时，Chill Guard 会播放提醒，并尝试隐藏你配置的应用。

## 仓库结构

- `chill_guard_app.py`：主程序
- `Chill Guard.spec`：macOS 打包用的 PyInstaller 配置
- `packaging/build_macos_release.sh`：macOS 发布脚本
- `docs/INSTALL.md`：英文安装指南
- `docs/INSTALL.zh-CN.md`：中文安装指南
- `yolo11s.pt`：打包默认模型文件
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
pip install -r requirements-dev.txt
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
```

- 涉及用户可见行为改动时，同时更新 `docs/INSTALL.md` 和 `docs/INSTALL.zh-CN.md`

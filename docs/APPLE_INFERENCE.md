# Apple 本地推理 / Apple on-device inference

本地开发分支新增 Core ML 支持。默认保持 PyTorch，Core ML 由用户选择；本改动未发布到 GitHub。当前转换和解码契约限定为 YOLO11 COCO 人体检测模型。Core AI 尚未接入本版本。

This development branch adds opt-in Core ML inference while retaining PyTorch as the default and fallback. The exporter/decoder support YOLO11 COCO detection models only. Core AI is outside this implementation.

## 准备模型 / Prepare a model

On an Apple silicon Mac with macOS 13+, in the repository's Python 3.12 environment:

```bash
pip install -r requirements-dev.txt -r requirements-coreml.txt
python tools/export_coreml.py --model yolo11s.pt --imgsz 1280
python chill_guard_app.py
```

在 Detection 中保留 `Model File = yolo11s.pt`、`Detect Size = 1280`，将 `Inference` 改为 `coreml` 或 `auto`，再应用设置。程序不会启动时下载或转换模型。更换检测尺寸时先重新导出；尺寸按 32 的倍数向上取整。替换现有导出需明确加 `--force`。

Keep Model File set to `yolo11s.pt` and Detect Size to 1280; select `coreml` or `auto` and apply settings. No model is downloaded or converted at runtime. Prepare another export for another detection size; sizes round up to a multiple of 32. Use `--force` explicitly to replace an export.

模型保存在 `.models/yolo11s-1280.mlpackage`，旁边的 JSON 记录源权重 SHA-256、尺寸和解码契约。加载时核对这些信息，避免使用过期或不匹配的导出。Core ML 使用固定方形 RGB 输入和原始检测头；Python 完成坐标还原与 NMS。CPU + Neural Engine 被允许参与，具体算子分配由 Core ML 决定。

The package and its JSON manifest live in `.models/`. The loader checks the source weights' SHA-256, input size, and decoder contract. Core ML uses square RGB input and a raw detection head; Python rescales boxes and performs NMS. CPU and Neural Engine are enabled; Core ML decides placement.

加载或推理失败时，本次监测切到 PyTorch 并显示原因；运行失败会用相同帧重试。为了保留原有 PyTorch 行为，回退后继续使用原来的矩形填充；它与 Core ML 的方形填充可能产生检测差异。640 输入配合远距离增强时，增强检测请求 1280，会触发回退。默认 1280 导出可用于两个检测流程。

Load/runtime failure switches the session to PyTorch with a visible reason; runtime failure retries the same frame. PyTorch preserves its original rectangular padding, which can differ from Core ML's square padding. Long-range boost requests at least 1280, so a 640-only export falls back. The default 1280 export handles both passes.

## 本地验证 / Local validation

```bash
python -m unittest discover -s tests -v
python tools/benchmark_inference.py image1.jpg image2.jpg --imgsz 1280 --iterations 20 --output validation/local/benchmark.json
python chill_guard_app.py --check-inference image1.jpg --backend coreml --report validation/local/check.json
```

这些命令只读取指定的本地图片，不打开摄像头，不播放声音，也不隐藏应用。检查报告中的实际后端与 `notice`；基准测试遇到回退会失败，避免把 PyTorch 的结果写成原生结果。详细实测与限制见 [验证记录](../validation/APPLE_INFERENCE_2026-10-08.md)。

These commands read local images only. They do not open the camera, play sounds, or hide apps. Check the actual backend and `notice`; benchmarks reject fallback instead of labeling PyTorch as native inference. See the [validation record](../validation/APPLE_INFERENCE_2026-10-08.md).

## 打包 / Packaging

```bash
./packaging/build_macos_release.sh
"dist/Chill Guard.app/Contents/MacOS/Chill Guard" --check-inference image1.jpg --backend coreml --report validation/local/frozen-check.json
```

PyInstaller 会包含已准备且带有 JSON 清单的 `.models/*.mlpackage`，以及两个内置 `.pt` 模型。无导出文件时仍可构建 PyTorch 版本。保留回退意味着仍包含 PyTorch；这次没有实现精简原生安装包，也没有更改签名、公证或发布流程。导出文件、环境、构建产物和原始验证输出都不提交到 Git。

PyInstaller includes prepared `.models/*.mlpackage` directories with matching manifests and both bundled `.pt` models. With no native export, it still builds the PyTorch app. Retaining fallback also retains PyTorch dependencies; this change does not shrink the app or change signing/notarization. Generated models, environments, builds, and raw validation outputs are excluded from Git.

技术依据 / Primary references: [Ultralytics Core ML](https://docs.ultralytics.com/integrations/coreml/), [Apple model prediction](https://apple.github.io/coremltools/docs-guides/source/model-prediction.html). Export arguments follow the repository's pinned Ultralytics 8.4.26, which uses `half=True`; newer documentation uses `quantize=16`.

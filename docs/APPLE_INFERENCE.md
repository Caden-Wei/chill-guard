# Apple 本地推理 / Apple on-device inference

本地 1.2 版默认使用 YOLO26s、Apple Core ML 和 1280 输入，保留 PyTorch 兼容回退。转换契约支持 YOLO26 与 YOLO11 的 COCO 80 类检测权重，只解码 person。Core AI 未接入。当前改动尚未推送到 GitHub。

The local 1.2 build defaults to YOLO26s, Apple Core ML and 1280 input, with a PyTorch fallback. The contract supports YOLO26 and YOLO11 COCO detection weights and decodes only person. Core AI is outside this implementation. These changes have not been pushed to GitHub.

## 准备模型 / Prepare a model

On Apple silicon, in the repository's Python 3.12 environment:

```bash
pip install -r requirements-dev.txt -r requirements-coreml.txt
python tools/export_coreml.py --model yolo26s.pt --imgsz 1280
python chill_guard_app.py
```

在「检测设置」选择 YOLO26s、Apple Core ML（推荐），检测尺寸为 1280，再保存更改。随应用提供的导出文件使用 FP16、固定方形 RGB 输入及原始 COCO 输出。程序不会在运行时下载或转换模型。更换尺寸时先导出对应模型；尺寸向上取整到 32 的倍数，替换现有导出须使用 `--force`。

In Detection, select YOLO26s and Apple Core ML (recommended), keep Detection size at 1280, and Save changes. The prepared export uses FP16, fixed square RGB input and raw COCO output. The app does not download or convert models at runtime. Export another size before selecting it; sizes round up to a multiple of 32. Replacing an export requires `--force`.

模型位于 `.models/yolo26s-1280.mlpackage`，JSON 清单记录源权重 SHA-256、尺寸、导出版本和解码契约。加载时验证权重、输入颜色与尺寸、输出结构。Ultralytics 8.4.174 的导出参数为 `quantize=16, nms=None`，获得 `(1, 84, 33600)` 输出；PyTorch 路径同样关闭 YOLO26 的端到端检测头，使用一对多头。Python 还原坐标并执行 NMS。Core ML 允许 CPU 与 Neural Engine 参与，具体算子分配由系统决定。

The `.models/` package and manifest record and validate weights SHA-256, size, export versions, RGB input and output contract. Pinned Ultralytics 8.4.174 uses `quantize=16, nms=None` for `(1, 84, 33600)` output. PyTorch also disables YOLO26's end-to-end head to use the one-to-many head. Python rescales boxes and runs NMS. CPU and Neural Engine are enabled; Core ML chooses placement.

加载或推理失败会显示原因并切到 PyTorch；运行失败会用同一帧重试一次。PyTorch 使用矩形填充，可能与 Core ML 的方形填充产生检测差异。远距离增强请求至少 1280，只有 640 导出时会回退。概览在待机时显示「已配置引擎」，运行时显示实际引擎。

Load or runtime failure visibly switches to PyTorch; runtime failure retries the same frame once. PyTorch's rectangular padding can produce different detections from Core ML's square padding. Long-range boost requests at least 1280, so a 640-only export falls back. Overview distinguishes the configured engine in standby from the actual engine during monitoring.

## 本地验证 / Local validation

```bash
python -m unittest discover -s tests -v
python tools/benchmark_inference.py image1.jpg image2.jpg --imgsz 1280 --iterations 30 --output validation/local/benchmark.json
python chill_guard_app.py --check-inference image1.jpg --backend coreml --report validation/local/check.json
```

推理诊断和基准仅读取指定图片，不打开摄像头、不播放声音、不隐藏应用。基准拒绝把回退结果标记为原生结果。YOLO26s 在本机两张样图的 Core ML 中位耗时约 34 ms，PyTorch MPS 约 33–42 ms；这不是检测准确率或所有场景的速度结论。此前 YOLO11s 的性能数字不代表 YOLO26s。详情见 [YOLO26 和界面验证记录](../validation/DESKTOP_AIR_2026-10-08.md)；旧版记录保留在 [YOLO11 验证](../validation/APPLE_INFERENCE_2026-10-08.md)。

Inference diagnostics and benchmarks only read images, with no camera, sounds or app hiding. Benchmarks reject fallback mislabeled as native inference. On two sample images on this Mac, YOLO26s Core ML median latency was about 34 ms and PyTorch MPS about 33–42 ms. These samples establish neither accuracy nor speed in every scene. Earlier YOLO11s numbers do not describe YOLO26s.

## 打包 / Packaging

```bash
./packaging/build_macos_release.sh
"dist/Chill Guard.app/Contents/MacOS/Chill Guard" --check-inference image1.jpg --backend coreml --report validation/local/frozen-check.json
```

PyInstaller 包含已准备且带 JSON 清单的 `.models/*.mlpackage`、三个 `.pt` 模型、CustomTkinter 的字体和主题资源及本机读取的界面图标。无原生导出时仍能构建 PyTorch 版本。保留兼容回退也会保留 PyTorch 依赖，因此本次没有缩小安装包。生成的模型包、环境、构建产物与原始验证输出不提交到 Git。签名、公证和公开发布流程没有改变。

PyInstaller includes prepared native packages with manifests, three `.pt` weights, CustomTkinter fonts/themes and UI icons. Without an export it still builds a PyTorch app. Fallback retains PyTorch dependencies, so the bundle is not reduced in size. Generated packages, environments, builds and raw reports are excluded from Git. Signing, notarization and public release procedures remain unchanged.

技术依据 / Primary references: [Ultralytics Core ML](https://docs.ultralytics.com/integrations/coreml/), [Apple prediction](https://apple.github.io/coremltools/docs-guides/source/model-prediction.html). The executable contract above is verified against the repository's pinned exporter.

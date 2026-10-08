"""Prepare a verified, offline YOLO11 COCO export for Chill Guard."""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from person_detector import input_size, model_digest, package_name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=Path("yolo11s.pt"))
    parser.add_argument("--imgsz", type=int, default=1280)
    parser.add_argument("--output-dir", type=Path, default=Path(".models"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not args.model.is_file() or args.model.suffix != ".pt":
        parser.error("--model must be an existing local .pt file")
    if not 320 <= args.imgsz <= 1600:
        parser.error("--imgsz must be between 320 and 1600")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    destination = args.output_dir / package_name(args.model, args.imgsz)
    manifest_path = Path(str(destination) + ".json")
    if (destination.exists() or manifest_path.exists()) and not args.force:
        parser.error("Export already exists; use --force to replace it")

    import coremltools
    import ultralytics
    from ultralytics import YOLO
    with tempfile.TemporaryDirectory(prefix="chill-coreml-") as directory:
        weights = Path(directory) / args.model.name
        shutil.copy2(args.model, weights)
        model = YOLO(str(weights), task="detect")
        architecture = Path(model.model.yaml.get("yaml_file", "")).name
        if (not architecture.startswith("yolo11") or model.model.model[-1].nc != 80
                or model.names.get(0) != "person"):
            parser.error("This adapter supports YOLO11 COCO person detection only")
        exported = Path(model.export(format="coreml", imgsz=input_size(args.imgsz),
                                     half=True, nms=False, dynamic=False, device="cpu"))
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(exported), destination)
    manifest_path.write_text(json.dumps({
        "schema_version": 1, "head": "yolo11-coco-raw", "imgsz": input_size(args.imgsz),
        "source_sha256": model_digest(args.model), "precision": "fp16",
        "ultralytics": ultralytics.__version__, "coremltools": coremltools.__version__,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {destination}; choose auto or coreml with Detect Size {input_size(args.imgsz)}.")


if __name__ == "__main__":
    main()

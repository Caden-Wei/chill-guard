#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
APP_NAME="Chill Guard.app"
APP_PATH="$DIST_DIR/$APP_NAME"
DMG_PATH="$DIST_DIR/Chill Guard-macOS.dmg"
STAGING_DIR="$(mktemp -d /tmp/chill_guard_release.XXXXXX)"
CLEAN_APP_DIR="$(mktemp -d /tmp/chill_guard_clean_app.XXXXXX)"
CLEAN_APP_PATH="$CLEAN_APP_DIR/$APP_NAME"

cleanup() {
  rm -rf "$STAGING_DIR"
  rm -rf "$CLEAN_APP_DIR"
}
trap cleanup EXIT

cd "$ROOT_DIR"

MPLCONFIGDIR=/tmp/mplcache PYINSTALLER_CONFIG_DIR=/tmp/pyinstaller_cache ./.venv/bin/python -m PyInstaller "Chill Guard.spec" --noconfirm
ditto "$APP_PATH" "$CLEAN_APP_PATH"
xattr -cr "$CLEAN_APP_PATH"
codesign --force --deep --sign - "$CLEAN_APP_PATH"
codesign --verify --deep --strict "$CLEAN_APP_PATH"

mkdir -p "$STAGING_DIR"
ditto "$CLEAN_APP_PATH" "$STAGING_DIR/$APP_NAME"
ln -s /Applications "$STAGING_DIR/Applications"

rm -f "$DMG_PATH"
hdiutil create -volname "Chill Guard" -srcfolder "$STAGING_DIR" -ov -format UDZO "$DMG_PATH"

echo "Built:"
echo "  $APP_PATH"
echo "  $DMG_PATH"

#!/bin/bash
# Patches mopidy and pidi-display-pil for Trixie (Debian 13) compatibility:
#   1. pidi-display-pil: Pillow 10+ removed getsize(), replaced with getbbox()
#   2. mopidy scan.py: GStreamer API change - StructureWrapper.get_structure(0).get_name()
#   3. mopidy stream/actor.py: catch AttributeError from scan.py alongside ScannerError

set -e

VENV="/home/pi/.virtualenvs/mopidy"
LIB="$VENV/lib/python3.13/site-packages"

# --- Patch 1: pidi-display-pil getsize() -> getbbox() ---
PIDI_FILE=$(find "$LIB" -name "__init__.py" -path "*/pidi_display_pil/*")
if [ -z "$PIDI_FILE" ]; then
    echo "ERROR: Could not find pidi_display_pil/__init__.py"
    exit 1
fi
echo "Patching $PIDI_FILE"
sed -i 's/font\.getsize(\(.*\))\[0\]/font.getbbox(\1)[2]/g' "$PIDI_FILE"
echo "  Done. Verify:"
grep -n "getsize\|getbbox" "$PIDI_FILE"

# --- Patch 2: mopidy scan.py GStreamer StructureWrapper ---
SCAN_FILE="$LIB/mopidy/audio/scan.py"
if [ ! -f "$SCAN_FILE" ]; then
    echo "ERROR: Could not find mopidy/audio/scan.py"
    exit 1
fi
echo "Patching $SCAN_FILE"
# Replace the old get_name() call with get_structure(0).get_name()
sed -i 's/mime = msg\.get_structure()\.get_value("caps")\.get_name()/caps = msg.get_structure().get_value("caps")\n                mime = caps.get_structure(0).get_name()/' "$SCAN_FILE"
echo "  Done. Verify:"
grep -n "get_structure\|get_name\|caps" "$SCAN_FILE" | grep -v "^.*#"

# --- Patch 3: mopidy stream/actor.py catch AttributeError ---
ACTOR_FILE="$LIB/mopidy/stream/actor.py"
if [ ! -f "$ACTOR_FILE" ]; then
    echo "ERROR: Could not find mopidy/stream/actor.py"
    exit 1
fi
echo "Patching $ACTOR_FILE"
sed -i 's/except exceptions\.ScannerError as exc:/except (exceptions.ScannerError, AttributeError) as exc:/' "$ACTOR_FILE"
echo "  Done. Verify:"
grep -n "ScannerError\|AttributeError" "$ACTOR_FILE"

echo ""
echo "All patches applied. Restart mopidy to take effect:"
echo "  systemctl --user restart mopidy"

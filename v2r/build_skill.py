"""`v2r build-skill`: zip skill/vid2reel/ into skill/vid2reel.zip for uploading to Claude."""

import zipfile

from v2r import ROOT

SKILL_DIR = ROOT / "skill" / "vid2reel"


def build():
    """Write the zip, with the vid2reel/ folder at its root as Claude's upload expects; return its path."""
    output = SKILL_DIR.with_suffix(".zip")
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(SKILL_DIR.rglob("*")):
            if path.is_file() and path.name != ".DS_Store":
                archive.write(path, path.relative_to(SKILL_DIR.parent))
    return output

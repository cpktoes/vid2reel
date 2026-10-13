# Licences

These are the libraries v2r uses beyond Python and FFmpeg. In the sandbox, pip downloads them each time; none of them is copied into this repo.

| Library | Version | Licence | Used for | Source |
| --- | --- | --- | --- | --- |
| Pillow | 12.3.0 | MIT-CMU | Opening photos, turning them upright and saving the full-size copy | https://github.com/python-pillow/Pillow |
| pillow-heif | 1.8.1 | BSD-3-Clause | Lets Pillow open iPhone HEIC photos | https://github.com/bigcat88/pillow_heif |
| pytest | 9.1.1 | MIT | Tests, on the Mac only (never installed in the sandbox) | https://github.com/pytest-dev/pytest |

pillow-heif's downloads include libheif and libde265 (LGPL-3.0) and x265 (GPL-2.0); this repo does not include or redistribute them.

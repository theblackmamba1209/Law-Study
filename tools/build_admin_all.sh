#!/bin/bash
# Administrative Code: OCR of the user's scan -> sections -> second witness (LawPhil) -> vote of three print readings -> scan-checked fixes
set -e
cd /home/claude/tools && python3 build_admin.py | grep -E "^(books|dropped|divisions)"
cd /home/claude/work/admx
python3 layout.py
python3 align.py | head -1
python3 merge.py
python3 adjudicate.py
python3 finalize.py

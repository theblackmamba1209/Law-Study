#!/bin/sh
# The whole build, in dependency order. build_data rewrites catalog.json, so everything that adds a key to the
# catalog (statutes, treaties, history, governing law, curriculum, coverage) runs after it.
set -e
cd /home/claude/tools
python3 errata_late.py > /dev/null
python3 build_data.py | tail -2
for n in notes_rpc1 notes_rpc2 notes_const2 notes_civil_oc notes_family notes_labor notes_ra9165 notes_ethics; do python3 $n.py > /dev/null; done
python3 build_shifts.py | tail -1
python3 build_enforce.py | tail -1
python3 build_statutes.py | tail -2
python3 build_treaties.py | tail -1
python3 build_history.py | tail -1
python3 build_govern.py | tail -1
python3 build_curriculum.py | tail -2
python3 -I cpra_cases.py | tail -1
python3 recent_data.py | tail -1
python3 build_coverage.py | tail -1
# stamp asset versions into index.html
cd /home/claude/site
JS=$(sha1sum assets/app.js | cut -c1-8); CSS=$(sha1sum assets/app.css | cut -c1-8)
sed -i -E "s/app\.js\?v=[0-9a-f]+/app.js?v=$JS/; s/app\.css\?v=[0-9a-f]+/app.css?v=$CSS/" index.html
grep -o 'app\.\(js\|css\)?v=[0-9a-f]*' index.html | tr '\n' ' '; echo

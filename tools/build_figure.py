"""The memory figure's anatomy.

Source: react-native-body-highlighter by Hicham Elabbassi (MIT licence; see vendor/react-native-body-highlighter-LICENSE.txt).
We use the front view of its male body: the outline and the muscle-group paths, regrouped for our eight places.
Output: data/figure.json
"""
import json, sys, shutil, os
SITE = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/site/data'
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f'{HERE}/vendor/body-front.json'))
P = d['parts']
def j(*keys):
    out = []
    for k in keys:
        slug, _, side = k.partition('.')
        for sd, arr in P[slug].items():
            if not side or sd == side:
                out += arr
    return ' '.join(out)
muscles = j('chest', 'obliques', 'abs', 'biceps', 'triceps', 'neck', 'trapezius', 'deltoids', 'adductors', 'quadriceps', 'knees', 'tibialis', 'calves', 'forearm', 'ankles')
fig = {
    'credit': 'Figure anatomy adapted from react-native-body-highlighter by Hicham Elabbassi, MIT licence.',
    'outline': d['outline'], 'muscles': muscles, 'head': j('head'), 'hair': j('hair'), 'hands': j('hands'), 'feet': j('feet'),
    'hl': {'lab': j('trapezius', 'deltoids'), 'eth': j('chest.right'), 'crim': j('hands.left'), 'com': j('hands.right'), 'intl': j('feet', 'ankles'), 'pol': j('head', 'hair'), 'craft': j('head')},
}
json.dump(fig, open(f'{SITE}/figure.json', 'w'), separators=(',', ':'))
shutil.copy(f'{HERE}/vendor/react-native-body-highlighter-LICENSE.txt', f'{SITE}/figure-LICENSE.txt')
print('figure.json', os.path.getsize(f'{SITE}/figure.json'), 'bytes')

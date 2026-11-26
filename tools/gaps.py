import sys, re, glob
sys.path.insert(0, '/home/claude/tools'); import parse_md as P
def gaps(provs):
    nums = []
    for p in provs:
        m = re.match(r'^(\d+)$', p['n'] or '')
        if m: nums.append(int(m.group(1)))
    out = []; seen = set(); dup = []
    for a in nums:
        if a in seen: dup.append(a)
        seen.add(a)
    if nums:
        missing = [i for i in range(min(nums), max(nums) + 1) if i not in seen]
    else: missing = []
    order = sum(1 for a, b in zip(nums, nums[1:]) if b < a)
    return missing, dup, order
for f in sys.argv[1:]:
    m, t, pre, d, p = P.parse(f, 'x')
    mi, du, od = gaps(p)
    print(f[:60], 'missing', mi[:40], len(mi), 'dup', du[:20], 'backsteps', od)

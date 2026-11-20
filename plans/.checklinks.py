import pathlib
import re
import subprocess

R = '/home/zh/www/'
REPOS = ['doc', 'personalCloud', 'dshSuperagentRepo', 'dsh-workbench',
         'dsh-context-guard', 'dsh-workflow-shortcuts',
         'personalCloud/task/superCreater', 'personalCloud/task/xctl']
bad = []
for repo in REPOS:
    try:
        files = subprocess.run(['git', '-C', R + repo, 'ls-files', '*.md'],
                               capture_output=True, text=True).stdout.splitlines()
    except Exception:
        continue
    for rel in files:
        p = pathlib.Path(R + repo + '/' + rel)
        if not p.exists():
            continue
        t = p.read_text(encoding='utf-8')
        for m in re.finditer(r'\]\(([^)\s]+)\)', t):
            tgt = m.group(1)
            if 'PLAN' not in tgt or '://' in tgt or tgt.startswith('#'):
                continue
            if tgt.startswith('/home/zh/www/'):
                q = pathlib.Path(tgt)
            elif tgt.startswith('/'):
                q = pathlib.Path(R + repo + tgt)
            else:
                q = (p.parent / tgt).resolve()
            if not q.exists():
                bad.append(f'{repo}/{rel}: {tgt}')
for b in bad:
    print(b)
print('TOTAL', len(bad))

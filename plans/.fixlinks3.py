import os
import pathlib
import re
import subprocess

R = '/home/zh/www/'
REPOS = ['doc', 'personalCloud', 'dshSuperagentRepo', 'dsh-workbench',
         'dsh-context-guard', 'dsh-workflow-shortcuts',
         'personalCloud/task/superCreater', 'personalCloud/task/xctl']

link_re = re.compile(r'\]\(([^)\s]+)\)')

for repo in REPOS:
    root = pathlib.Path(R + repo)
    for p in sorted(root.glob('plans/**/*.md')) + sorted(root.glob('plans/*.md')):
        if '/archive/' in str(p):
            continue
        rel = str(p.relative_to(root))
        if not (rel.startswith('plans/') or rel.endswith('PLAN-xctl-roadmap.md') or '/plans/' in rel):
            continue
        t = p.read_text(encoding='utf-8')
        o = t

        def fix(m):
            tgt = m.group(1)
            if tgt.startswith(('http', '#', '/')) or not tgt:
                return m.group(0)
            cand = (p.parent / tgt).resolve()
            if cand.exists():
                return m.group(0)
            rootcand = (root / tgt).resolve()
            if rootcand.exists():
                new = os.path.relpath(rootcand, p.parent.resolve())
                return '](' + new + ')'
            ar = (root / 'plans/archive' / tgt).resolve()
            if ar.exists():
                new = os.path.relpath(ar, p.parent.resolve())
                return '](' + new + ')'
            return m.group(0)

        t = link_re.sub(fix, t)
        # drop body status lines (state lives in frontmatter)
        t = re.sub(r'(?m)^\s*(?:>\s*)?-\s*状态[:：].*\n', '', t)
        t = re.sub(r'(?m)^>\s*状态[:：].*\n', '', t)
        if t != o:
            p.write_text(t, encoding='utf-8')
            print('fixed', repo, rel)

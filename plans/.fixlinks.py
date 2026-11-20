import pathlib, subprocess, sys

R = '/home/zh/www/'

MOVES = {
 'doc/plans/PLAN-republish-plugin-market.md': 'doc/archive/plans/PLAN-republish-plugin-market.md',
 'personalCloud/PLAN-experience-review-supervise.md': 'personalCloud/plans/archive/PLAN-experience-review-supervise.md',
 'personalCloud/PLAN-file-transfer.md': 'personalCloud/plans/archive/PLAN-file-transfer.md',
 'personalCloud/doc/PLAN-personal-sync-refresh.md': 'personalCloud/plans/archive/PLAN-personal-sync-refresh.md',
 'personalCloud/task/dsh-token-control/PLAN-20261118-ops-token-value.md': 'personalCloud/plans/archive/PLAN-token-control-ops-token-value.md',
 'personalCloud/task/dsh-workflow-shortcuts/PLAN-ok-no-auto-archive-prompts.md': 'personalCloud/plans/archive/PLAN-dsh-workflow-shortcuts-no-auto-archive.md',
 'personalCloud/task/health-watch/PLAN-2026-11-16-noise-reduction.md': 'personalCloud/plans/archive/PLAN-health-watch-noise-reduction.md',
 'personalCloud/doc/PLAN-session-task-isolation.md': 'personalCloud/plans/PLAN-session-task-isolation.md',
 'personalCloud/task/dsh-token-control/PLAN-20261118-ops-3day-trial-and-ptc.md': 'personalCloud/plans/PLAN-token-control-ops-3day-trial-and-ptc.md',
 'personalCloud/task/dsh-workspace-symlink/PLAN-workspace-file-symlink.md': 'personalCloud/plans/PLAN-workspace-file-symlink.md',
 'personalCloud/task/nextcloud-storage-1t/PLAN-nextcloud-storage-1t.md': 'personalCloud/plans/PLAN-nextcloud-storage-1t.md',
 'personalCloud/task/notes/PLAN-obsidian-trial-20261120.md': 'personalCloud/plans/PLAN-obsidian-trial-20261120.md',
 'personalCloud/task/project-experience-watch/PLAN-personalcloud-watch.md': 'personalCloud/plans/PLAN-personalcloud-watch.md',
 'personalCloud/task/superCreater/PLAN-creator-tg-targeting.md': 'personalCloud/task/superCreater/plans/PLAN-creator-tg-targeting.md',
 'personalCloud/task/xctl/docs/PLAN.md': 'personalCloud/task/xctl/plans/PLAN-xctl-roadmap.md',
 'dshSuperagentRepo/doc/PLAN-dsh-immersive-glass.md': 'dshSuperagentRepo/plans/archive/PLAN-dsh-immersive-glass.md',
 'dshSuperagentRepo/doc/PLAN-dsh-immersive-glass-scope-fix.md': 'dshSuperagentRepo/plans/archive/PLAN-dsh-immersive-glass-scope-fix.md',
 'dshSuperagentRepo/doc/PLAN-sa-thread-sessions.md': 'dshSuperagentRepo/plans/archive/PLAN-sa-thread-sessions.md',
 'dshSuperagentRepo/doc/PLAN-sa-thread-sessions-closeout.md': 'dshSuperagentRepo/plans/archive/PLAN-sa-thread-sessions-closeout.md',
 'dshSuperagentRepo/workdir-rag/docs/PLAN.md': 'dshSuperagentRepo/plans/archive/PLAN-workdir-rag.md',
 'dshSuperagentRepo/task/project-experience/PLAN.md': 'dshSuperagentRepo/plans/PLAN-project-experience-compiler.md',
 'dshSuperagentRepo/task/project-experience-watch/PLAN.md': 'dshSuperagentRepo/plans/PLAN-project-experience-watch.md',
 'dsh-workbench/PLAN-archived-session-display.md': 'dsh-workbench/plans/archive/PLAN-archived-session-display.md',
 'dsh-workbench/PLAN-todo-marker-fallback.md': 'dsh-workbench/plans/archive/PLAN-todo-marker-fallback.md',
 'dsh-workbench/PLAN-todo-user-action.md': 'dsh-workbench/plans/archive/PLAN-todo-user-action.md',
 'dsh-workbench/PLAN-dsh-workbench.md': 'dsh-workbench/plans/PLAN-dsh-workbench.md',
 'dsh-workbench/PLAN-sa-ui-migration.md': 'dsh-workbench/plans/PLAN-sa-ui-migration.md',
 'dsh-workbench/PLAN-todo-title-listener-fix.md': 'dsh-workbench/plans/PLAN-todo-title-listener-fix.md',
 'dsh-context-guard/PLAN.md': 'dsh-context-guard/plans/PLAN-context-guard.md',
 'dsh-context-guard/PLAN-call-limits.md': 'dsh-context-guard/plans/archive/PLAN-call-limits.md',
 'dsh-context-guard/PLAN-continue-draft-on-hard-limit.md': 'dsh-context-guard/plans/archive/PLAN-continue-draft-on-hard-limit.md',
 'dsh-context-guard/PLAN-risk-always-allow-fix.md': 'dsh-context-guard/plans/archive/PLAN-risk-always-allow-fix.md',
 'dsh-context-guard/PLAN-rm-opt-whitelist.md': 'dsh-context-guard/plans/archive/PLAN-rm-opt-whitelist.md',
 'dsh-context-guard/PLAN-temp-rm-step-wording.md': 'dsh-context-guard/plans/archive/PLAN-temp-rm-step-wording.md',
 'dsh-workflow-shortcuts/PLAN-configurable-spec-paths.md': 'dsh-workflow-shortcuts/plans/archive/PLAN-configurable-spec-paths.md',
 'dsh-workflow-shortcuts/PLAN-dg-plan-title.md': 'dsh-workflow-shortcuts/plans/archive/PLAN-dg-plan-title.md',
 'dsh-workflow-shortcuts/PLAN-g-empty-recent-plan.md': 'dsh-workflow-shortcuts/plans/archive/PLAN-g-empty-recent-plan.md',
 'dsh-workflow-shortcuts/PLAN-g-event-entry-shape.md': 'dsh-workflow-shortcuts/plans/archive/PLAN-g-event-entry-shape.md',
 'dsh-workflow-shortcuts/PLAN-g-session-title-from-plan.md': 'dsh-workflow-shortcuts/plans/archive/PLAN-g-session-title-from-plan.md',
}

def tracked(repo):
    out = subprocess.run(['git', '-C', repo, 'ls-files', '*.md'],
                         capture_output=True, text=True).stdout.splitlines()
    return out

for repo in ['doc', 'personalCloud', 'dshSuperagentRepo', 'dsh-workbench',
             'dsh-context-guard', 'dsh-workflow-shortcuts']:
    changed = []
    for rel in tracked(repo):
        if '/archive/' in rel or rel.startswith('plans/') or '/plans/' in rel and rel.endswith('PLAN-') is False:
            pass
        p = pathlib.Path(R) / repo / rel
        if not p.exists():
            continue
        t = p.read_text(encoding='utf-8')
        o = t
        for old, new in MOVES.items():
            t = t.replace(R + old, R + new)
        if t != o:
            p.write_text(t, encoding='utf-8')
            changed.append(rel)
    print(repo, len(changed), changed[:12])

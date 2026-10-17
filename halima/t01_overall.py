import pandas as pd
gt = pd.read_csv(r'ground-truth\master.csv', keep_default_na=False)
norm = lambda s: s.split(':',1)[-1].strip().lower()
jobs = [("Entra User","live-entra-users.csv"),("Entra Group","live-entra-groups.csv"),("Entra App","live-entra-apps.csv"),("Entra Alias","live-entra-aliases.csv"),("GitHub Repo","live-github-repos.csv"),("GitHub Team","live-github-teams.csv"),("Slack Channel","live-slack-channels.csv"),("Jira Project","live-jira-projects.csv"),("Jira Component","live-jira-components.csv"),("n8n Workflow","live-n8n-workflows.csv")]
tot = hit = 0
for p, f in jobs:
    try: live = pd.read_csv('halima/' + f, keep_default_na=False)
    except FileNotFoundError:
        print(p, "-> live file missing, skipped"); continue
    g = set(gt[gt.Asset.str.startswith(p)].Asset.map(norm)); l = set(live.iloc[:,0].map(norm))
    h = len(g & l); tot += len(g); hit += h
    print(f"{p}: {h}/{len(g)}")
print(f"OVERALL: {hit}/{tot} = {hit/tot*100:.1f}%")

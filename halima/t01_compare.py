import sys, pandas as pd
prefix, live_file = sys.argv[1], sys.argv[2]
gt = pd.read_csv(r'ground-truth\master.csv', keep_default_na=False)
gt = gt[gt.Asset.str.startswith(prefix)]
norm = lambda s: s.split(':',1)[-1].strip().lower()
gt_set = set(gt.Asset.map(norm))
live = pd.read_csv(live_file, keep_default_na=False)
live_set = set(live.iloc[:,0].map(norm))
hit = gt_set & live_set
print(f"{prefix}: {len(hit)}/{len(gt_set)} = {len(hit)/len(gt_set)*100:.1f}%")
print("Missing in live:", sorted(gt_set-live_set))
print("Extra in live:", sorted(live_set-gt_set))

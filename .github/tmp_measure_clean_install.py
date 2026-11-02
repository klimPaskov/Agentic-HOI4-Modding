import importlib.util, json, sys
from pathlib import Path
boot_path, prefix, version = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
spec = importlib.util.spec_from_file_location("b", boot_path)
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
node, _ = b.resolve_node_and_npm()
prefix.mkdir(parents=True, exist_ok=False)
with b.pinned_npm_runtime() as rt:
    out = b.npm(node, rt, ["view", f"hoi4-agent-tools@{version}", "dist.integrity", "--json"])
    integrity = json.loads(out)
    print("integrity", integrity)
    b.npm(node, rt, ["install", "--global", "--prefix", str(prefix), "--ignore-scripts", "--no-audit", "--no-fund", f"hoi4-agent-tools@{version}"], timeout=1800)
print("installed", prefix)

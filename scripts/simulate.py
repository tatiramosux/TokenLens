"""Produce demonstration data without CLI discovery, credentials or network."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tokenlens.store import Store
from lab.demo import seed

if __name__ == "__main__":
    p=argparse.ArgumentParser(description="Somente dados sinteticos; nao chama provedores.")
    p.add_argument("--db",type=Path,default=Path(".local/synthetic.sqlite3"))
    args=p.parse_args()
    store=Store(args.db)
    seed(store)
    print(f"{len(store.events(True))} medicoes sinteticas. Nenhuma CLI executada.")

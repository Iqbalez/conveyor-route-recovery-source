"""Reproduce a tiny, non-benchmark example without the creator's private key."""
import hashlib
from pathlib import Path

import generate

here = Path(__file__).resolve().parent
generate.ROOT = here
generate.N_SHIFTS = 4
(here / "reports").mkdir(exist_ok=True)
demo_key = hashlib.sha256(b"conveyor-route-recovery-public-demo-only-v1").digest()
generate.generate(here / "demo_raw", demo_key)
print("Demo only: demo_raw/shifts.csv is separate from the frozen challenge corpus.")

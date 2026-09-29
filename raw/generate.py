"""Create the original anonymous conveyor scan corpus.

The private master key is creator-only and is not part of the upload. Raw
shifts.csv is the authoritative source for deterministic preparation.
"""
import argparse
import csv
import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
N_SHIFTS = 4000
N_PARCELS = 40
CHANNELS = 6
BANKS = 4
MATRIX_RNG = np.random.default_rng(1441)
MATRICES = []
for bank in range(BANKS):
    matrix = MATRIX_RNG.uniform(0.0, 0.36, (CHANNELS, CHANNELS))
    matrix += np.eye(CHANNELS) * MATRIX_RNG.uniform(0.55, 1.25, CHANNELS)
    matrix /= matrix.sum(axis=1, keepdims=True)
    MATRICES.append(matrix)


def derive(master, purpose, index):
    return hmac.new(master, purpose + index.to_bytes(8, "big"), hashlib.sha256).digest()


def simulate(master, index):
    seed = int.from_bytes(derive(master, b"simulation", index)[:8], "big")
    rng = np.random.default_rng(seed)
    n = N_PARCELS
    latent = rng.dirichlet(np.full(CHANNELS, 1.7), size=n) * CHANNELS
    route = rng.integers(0, 4, size=n)
    true_time = np.cumsum(rng.exponential(0.52, size=n))
    banks = []
    for bank in range(BANKS):
        if bank:
            step = rng.choice([-1, 0, 1], size=n, p=[0.22, 0.56, 0.22])
            next_route = np.clip(route + step, 0, 3)
            lane_delay = rng.uniform(-0.35, 0.35, size=4)
            planned = true_time + 4.4 + 0.9 * abs(next_route - route) + lane_delay[next_route] + rng.normal(0, 0.65, n)
            for lane in range(4):
                member = np.flatnonzero(next_route == lane)
                member = member[np.argsort(planned[member], kind="mergesort")]
                last = -np.inf
                for parcel in member:
                    planned[parcel] = max(planned[parcel], last + 0.68)
                    last = planned[parcel]
            true_time = planned
            route = next_route
        gain = rng.lognormal(0, 0.24, CHANNELS)
        offset = rng.normal(0, 0.16, CHANNELS)
        channels = (latent @ MATRICES[bank].T) * gain + offset + rng.normal(0, 0.29, (n, CHANNELS))
        measured_time = true_time + rng.normal(0, 0.38, n)
        rows = [
            {
                "parcel": int(parcel),
                "lane": int(route[parcel]),
                "time": float(round(measured_time[parcel], 4)),
                "channels": [float(round(v, 4)) for v in channels[parcel]],
            }
            for parcel in range(n)
        ]
        rng.shuffle(rows)
        for row in rows:
            row["scan_id"] = "x_" + rng.bytes(10).hex()
        banks.append(rows)
    shift_id = "s_" + derive(master, b"shift-id", index).hex()[:20]
    return {"shift_id": shift_id, "banks": banks}


def generate(root, master):
    began = time.perf_counter()
    root.mkdir(parents=True, exist_ok=True)
    shifts = [simulate(master, i) for i in range(N_SHIFTS)]
    shifts.sort(key=lambda item: item["shift_id"])
    scan_ids = [row["scan_id"] for shift in shifts for bank in shift["banks"] for row in bank]
    assert len({shift["shift_id"] for shift in shifts}) == N_SHIFTS
    assert len(scan_ids) == len(set(scan_ids)) == N_SHIFTS * BANKS * N_PARCELS
    path = root / "shifts.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["shift_id", "bank0", "bank1", "bank2", "bank3"])
        for shift in shifts:
            writer.writerow(
                [shift["shift_id"]]
                + [json.dumps(rows, separators=(",", ":"), ensure_ascii=False) for rows in shift["banks"]]
            )
    report = {
        "status": "MEASURED_GENERATION",
        "version": "3.0.0",
        "shifts": N_SHIFTS,
        "parcels_per_shift": N_PARCELS,
        "banks": BANKS,
        "raw_scans": len(scan_ids),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "master_key_sha256": hashlib.sha256(master).hexdigest(),
        "runtime_seconds": time.perf_counter() - began,
    }
    (ROOT / "reports" / "GENERATION_REPORT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "raw")
    parser.add_argument("--master-key-file", type=Path, default=ROOT / "research" / "PRIVATE_MASTER_KEY.hex")
    args = parser.parse_args()
    if not args.master_key_file.exists():
        args.master_key_file.write_text(secrets.token_hex(32) + "\n", encoding="ascii")
    master_key = bytes.fromhex(args.master_key_file.read_text(encoding="ascii").strip())
    if len(master_key) != 32:
        raise ValueError("Creator master key must contain exactly 32 bytes")
    generate(args.raw_dir, master_key)

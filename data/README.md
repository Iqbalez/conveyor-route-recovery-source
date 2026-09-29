# Anonymous Conveyor Scan Logs — observation-only source data

These four CSV parts contain the actual 4,000 shifts and 640,000 scans in the Conveyor Route Recovery challenge’s frozen corpus. They are the public-feature version of that corpus: each row has case_id,bank0,bank1,bank2,bank3, and each bank contains 40 scan objects with scan_id,time,lane,channels. Each part has 1,000 rows. Their union is exactly the 3,000 training-feature and 1,000 evaluation-feature rows produced by prepare.py; SAFE_DATA_MANIFEST.json records hashes.

The data are an original creator-owned simulation. The registered creator-side shifts.csv additionally contains parcel identity, which supplies hidden correspondence targets. Parcel identity, private answers and the master generation key are not published here. These observation files contain no target mappings or predictions. The complete six-file raw creator upload is provided separately to the platform for deterministic preparation.

The original generator, raw provenance, release metadata and CC0 data notice are in raw/ in this repository. The simulated data and observation-only publication are CC0 1.0; the generator code is MIT. No third-party dataset or personal data was used.

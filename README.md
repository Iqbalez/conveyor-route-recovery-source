# Conveyor Route Recovery — original source

Original creator-owned simulation for the Conveyor Route Recovery challenge, version 3.0.0. Four scanner banks observe forty parcels per independent shift. The challenge asks solvers to recover each exit scan's bank-0, bank-1 and bank-2 observations. This is simulated data, not measured factory performance.

The registered raw dataset is uploaded separately to the challenge platform. This public repository excludes the frozen raw CSV, the creator master key, private answers, evaluation labels, model predictions and local reports. Publishing those files could expose held-out targets.

The original generator is in `raw/generate.py`. The frozen raw ZIP contains 4,000 shifts and was created with a private 256-bit master key; the generator alone cannot reproduce that key or those exact shifts. `raw/GENERATION_METADATA.json` records its versions and SHA256 commitments. GitHub's editor normalizes the generator to LF line endings, while its frozen raw-ZIP SHA256 refers to the original CRLF bytes; the source text is otherwise identical. A safe public demonstration is in `raw/generate_demo.py` and uses a separate example key. The code is MIT-licensed; the original simulated data are CC0 1.0.

The challenge's `prepare.py` makes a deterministic 3,000/1,000 whole-shift train/evaluation split. The score is exact complete-history accuracy from 0 to 1. Public training inputs and labels may be used for fitting; evaluation observations are inference-only. `prepare.py`, `grade.py`, the raw ZIP, and participant documents are delivered in the platform challenge upload. This repository documents the dataset's origin and licenses.

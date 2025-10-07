# Sauce Labs Session Race Repro

Universal Python scripts to reproduce the free-tier minute deduction bypass vuln (race condition on session stop/start post-warning). Run on a low-mins account (~6-10 left), screenshot dashboard "Remaining Minutes" before/after—expect no/full deduction for overrun time.

## Quick Setup
- `pip install -r requirements.txt` (just requests)
- Hardcode creds in main.py or run with args.

## Usage (main.py - Universal)

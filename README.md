# Sauce Labs Session Race Repro

Universal Python scripts to reproduce the free-tier minute deduction bypass vuln (race condition on session stop/start post-warning). Run on a low-mins account (~6-10 left) or a new account, screenshot dashboard "Remaining Minutes" before/after—expect no/full deduction for overrun time.

## Quick Setup
- `pip install -r requirements.txt` (just requests)
- Hardcode creds in main.py or run with args.

## Usage (main.py - Universal)
- `--wait_minutes`: Tweak to hit post-3-min warning (e.g., 7 for 10-min limit overrun).
- Output: Initial/final usage snaps. "JACKPOT!" = vuln confirmed (no deduction).

## Usage (repro_v1.py - Hardcoded Backup)
Swap creds at top, `python repro_v1.py`. Same flow, fixed 7-min wait.

## Expected Flow
1. Start Chrome session (WebDriver API).
2. Burn wait time (past warning threshold).
3. Stop job (race trigger—deduction lags).
4. Instant new session (bypasses update).
5. Check: If mins unchanged, exploit wins.

## Proof Harvest
- Pre-run: Screenshot Sauce dashboard usage.
- Post-run: Screenshot again + console logs.
- Share this repo with H1 for validation.


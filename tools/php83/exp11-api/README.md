# exp11 isolated artifact regression

These harnesses remain **not executed** until the independently verified exp11
ZIP SHA-256 is placed in `artifact-sha256.txt`. The file is intentionally absent
during preparation. Missing/malformed pins fail before staging can contact a VM;
there is no placeholder artifact hash or implicit exp10 fallback.

- API: original74, original83 (required signature-fatal control), exp10/83,
  exp11/83; identical HTTP/trusted-HTTPS golden responses and negative CA checks.
- CLI: original74 has 12 rows; original83/exp10/exp11 have 36 total rows.
- Separate actual-exp11 class corpus: three PHP8.3 processes, 68 cases, linked
  to the previous three-class differential corpus. Runs on baseline74's copied
  PHP8.3 runtime, not the concurrently owned php83lab.

Both candidate ZIPs reject whole-artifact PHP7.4 execution. Existing exp10 harness,
stages and fixtures are not modified. Full candidate source verification is
repeated after API/CLI/class runs. Full application, FPM/AIO, services, performance,
packages and release acceptance remain outside this bounded corpus.

Stage once with `stage.sh 74` / `stage.sh 83`, only with explicit coordinator lab
ownership. Fresh-directory guards prevent replacing earlier stages. API runs
require exclusive baseline74 ownership, create one synthetic MariaDB per collector
and stop its known unit in finally. CLI/class tests need no SQL.

See `doc/php83/evidence/exp11-runtime/plan.md` for exact commands and limitations.

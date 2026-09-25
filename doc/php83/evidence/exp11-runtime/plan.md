# exp11 runtime integration plan

**Prepared, not executed.** No VM, SQL, application, package, CI, production or
release operation was performed while preparing these harnesses.

## Artifact prerequisite

The independently verified exp11 archive must exist at:

```text
/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts/exp11/Rigel-18.20.0-php83-experimental.exp11.zip
```

Only after independent byte/source/manifest verification, the coordinator writes
its actual 64-character lowercase SHA-256 plus newline to
`tools/php83/exp11-api/artifact-sha256.txt`. It is currently intentionally absent.
The stage validates it before any SSH call and checks the local ZIP against it;
remote extraction/verifiers and CLI collector use the same explicit pin. Missing
or malformed pins are errors, never passes or implicit prior-artifact fallback.

## Ownership and exact commands

Obtain **exclusive baseline74 ownership**, then create its fresh stage once:

```sh
bash tools/php83/exp11-api/stage.sh 74
```

The script guards hostname, creates `/home/vagrant/php-exp11-regression` with
plain mkdir (existing directory is an error), transfers the verified public ZIP,
unchanged patch-test fixtures, the new harness and frozen curly-offset probe,
then extracts it. It does not change previous stages or system PHP selection.
Separately, only the coordinator's php83lab owner may run:

```sh
bash tools/php83/exp11-api/stage.sh 83
```

Collect outputs into **new filenames**, retaining stdout/stderr and actual exit:

```sh
# baseline74 exclusive; owns synthetic DB and stops it in finally.
python3 tools/php83/exp11-api/collect.py \
  doc/php83/evidence/exp11-runtime/api-primary.json

# baseline74, after API collector has finished and released its SQL unit.
ssh -T -F /tmp/kaltura-php74-ssh.conf baseline74 \
  'python3 /home/vagrant/php-exp11-regression/exp11-regression/batch.py' \
  > doc/php83/evidence/exp11-runtime/cli74-primary.json

# Separate 3-class corpus on baseline74 copied PHP8.3; no SQL.
python3 tools/php83/exp11-api/collect-curly.py \
  doc/php83/evidence/exp11-runtime/curly-primary.json

# php83lab owner only; do not compete with candidate whole-tree scans.
ssh -T -F /tmp/kaltura-php83-ssh.conf php83 \
  'python3 /home/vagrant/php-exp11-regression/exp11-regression/batch.py' \
  > doc/php83/evidence/exp11-runtime/cli83-primary.json
```

The SSH examples illustrate the command; callers must additionally refuse
existing output paths and retain stderr/exit status. API/class collectors refuse
existing JSON reports themselves. Independent Claude/OpenCode/Cursor roles and VM
ownership are assigned by the coordinator, not by this prepared harness.

## Exact retained contracts

API has four rows: original74 baseline, original83 expected KalturaPDO signature
fatal, exp10 on PHP8.3, exp11 on PHP8.3. Successful rows must have exactly the
existing session/authentication HTTP+trusted-HTTPS output and reject the untrusted
CA. Unexpected stdout is hashed rather than persisted. Logs retain diagnostic
locations/counts and bounded fixture runtime observations, never raw KS logs.
Full exp11 and exp10 extracted-source verification repeats after SQL cleanup.

CLI retains 48 rows: six cases × standard/minimal INI, original74 (12), and
original83/exp10/exp11 (36). Original83's four historical JSON-fatal controls remain
expected; the remaining positive contracts must be independently compared.
A zero batch-process exit means collection finished, not every row passed.
No whole exp10/exp11 execution on PHP7.4 is supported.

The separate actual-exp11 corpus executes the same two Google_Utils versions
in separate processes and HTMLPurifier_Encoder (20+20+28 cases). Full exp11 source
bytes are checked before/after. Loaded class hashes must match the held lexical
candidate source identities; exact output is compared to the prior PHP8.3 class
corpus, whose probe hash must equal the unchanged staged probe. This links to the
previous original74/candidate74/candidate83 differential results; it does not
rerun all three variants or claim 63 modified files are behaviorally covered.

## Local checks and remaining limitations

Twenty-five local tests pass: ten fault-injected API matrix/cleanup controls, five
artifact-pin controls, and ten bounded additional-corpus controls. Shell syntax and Python compilation pass.
These tests make no SSH/database calls. Results are in `preparation-with-additions.*`.

No runtime success is asserted yet. Existing SSH host-key policy and copied PHP
runtime provenance are inherited; this preparation does not add cryptographic
host authentication or fresh binary/module attestation to the API/CLI collectors.
The separate `runtime-identity.py` helper now supplies fresh baseline74 native
PHP7.4 and copied PHP8.3 binary/module/linked-library hashes, Apache binary/modules,
standard/minimal runtime module lists and PHP7.4 CLI INI file hashes (no config
values). Run it immediately before and after the API/CLI/class sequence:

```sh
python3 tools/php83/exp11-api/runtime-identity.py \
  doc/php83/evidence/exp11-runtime/runtime-before.json
# Execute the owned baseline74 matrix above, serially.
python3 tools/php83/exp11-api/runtime-identity.py \
  doc/php83/evidence/exp11-runtime/runtime-after.json
```

Compare the full two JSON identity records; an unexplained change is not a pass.
This helper is prepared but not yet executed, and itself fails before SSH while
the exp11 pin is missing. It reads/hashes reviewed lab runtime files and invokes
only PHP version/module/INI inspection, not application code. API's existing
`PROBE_RUNTIME` observations remain retained. Prior behavior evidence alone is
not a fresh runtime identity attestation.

The API helper retains inherited limitations: synthetic schema/session resets,
no enabled external APC/cache/monitoring services, no full installed AIO/FPM,
no persistence/revocation workflow or performance benchmark. A transport/hash or
startup error can abort before a final report; missing reports are not passes.
Compiler diagnostics and all remaining static/reachability issues stay open.
No package, main merge, release or production permission follows from this plan.

## Four newly selected source repairs

After baseline74 API/CLI/class completion, while retaining exclusive ownership:

```sh
python3 tools/php83/exp11-api/collect-additions.py \
  doc/php83/evidence/exp11-runtime/additions-primary.json
```

This runs 17 actual-artifact processes (16 positive, one expected fatal), with
exact byte comparison to pinned prior independent Claude corpora. It includes
147 ternary cases, six autoload cases and ten composition cases. Runtime
identities must bracket this execution as well. This is not a new independent
golden corpus or approval of all source repairs.

# Authenticated HTTPS100, next diagnostic round

Root installed and independently verified scoped TLS R2 after successful HTTP
untimed100 R2. Do not rerun an old authenticated harness lacking the TLS log
adapter: TLS access/error files are outside its original log roots.

After independent review, root runs `run_https.py --check`, then
`run_https.py --output NEW_EXCLUSIVE_DIRECTORY`. Fresh immutable stage is
`/var/lib/kaltura-baseline-https100-r1`. Historical stages and receipts remain
unchanged. Only the root coordinator executes native commands.

Both active PostTransport construction sites now use exact .74, HTTPS and8443,
with the approved CA PEM SHA256. Existing Origin explicitly permits8443; no
transport library or port allowlist was widened. CA bytes are read through the
vetted root-private file reader, verified before any network credential request.
There is no HTTP fallback, proxy inheritance, redirect forwarding or disabled
certificate/hostname verification.

The unchanged TLS inventory adapter d67eb659… is loaded and pinned before any
credential read or request, including invalidnonce. It wraps legacy.logs globally
for this isolated collector process, so every original snapshot, rescan, quiet
settle and common-end check includes exact root600 TLS access/error sinks. The
adapter rechecks metadata on each call; absent/malformed/extra sinks are failures.
Original source/config drift, invalid-secret-before-real-secret, USER-only,
34/33/33 accounting and all-token finite scans remain mandatory. The unchanged
bounded settle does not advance pre-request scanner boundaries. Every token
batch must cover a common unchanged file/journal end.

Output adds only fixed scheme/port/public CA hash and the declared complete TLS
inventory flag; success also requires100 passing operations and all privacy
checks. It remains an untimed diagnostic, not a warmup/measured sample or full
baseline acceptance. Host RuntimeMax/outer capture remain bounded; timeout,
worker cleanup, redirection, certificate or late-log failures are not passes.

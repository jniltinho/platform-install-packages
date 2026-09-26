# Baseline protocol client preparation

`guarded_http.py` is a local-only preparation building block, not the installed-AIO
runner and not baseline acceptance. It never defaults to `.20`; the origin fixes
one literal lab IP, transport and port. Every nested URI must use `Origin.resolve`.
Redirects are refused, ambient proxies disabled and HTTPS requires a pinned CA.
Response byte limits and declared lengths are checked; errors omit request URLs.

Current GET-only interface has no KS/authentication, uploads, API POST, HLS parser,
Range contract, browser, retries or benchmark statistics. It has a **socket timeout,
not a hard whole-request deadline**: a slowly streaming response can exceed that
wall time. A bounded subprocess or reviewed total-deadline transport must be added
before the real baseline workload; do not call the present timeout a total bound.
TLS success/wrong-CA and redirect/no-forwarding transport need real isolated local
server execution; current tests mock the opener and exercise pure guards only.
No network request or VM run has occurred in this preparation.

Run `python3 -m unittest discover -s tools/php83/baseline-protocol -p 'test_*.py' -v`.
Keep older `tools/php83/lab_target.py` and historic evidence unchanged. Future API
credentials remain in guest memory/private files, never CLI arguments, requests in
public logs, manifests or result reports. Local synthetic test marker strings are
not real credentials.

`freeze_media.py` prepares the Decision7 source fixtures with explicit commands,
frame counts and predeclared one-video-frame plus one-AAC-frame duration tolerance.
It was executed after independent command review; both resulting files passed
independent actual ffprobe validation. See doc/php83/baseline-media.md. The prior
NOT_EXECUTED state is retained in the historical reviews. It refuses an existing
directory, never overwrites media, hashes exact encoder/prober binaries and records
versions/commands/results. Linked-library/host identities are not yet attested by
this script. Copy identical validated bytes to labs later; single-threaded encoding
is not a claim of byte reproducibility across encoder builds. It creates technical
test patterns only, not user media or a creative video deliverable.

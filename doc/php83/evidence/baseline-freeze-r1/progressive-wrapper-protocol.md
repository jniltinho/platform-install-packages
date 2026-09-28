# Short original progressive wrapper (local candidate)

No native execution by author. Root owns the VM and execution.

This derivative replaces the prior one-flavor-list observation with one native
`flavorasset.getUrl` for the owned original asset, followed by a full source GET
and two 1024-byte ranges. It does not repeat the 100-call workload, upload, decode,
fetch HLS, change profiles, or claim complete task acceptance.

The existing source/entry/USER/TLS observation and saved privacy start are retained.
The native URL is never rewritten. Queries, credential path markers and current
secret/KS (including decoded variants) are rejected before GET. Bounded returned
long token candidates remain private and join the failure/success privacy scans,
because getUrl can itself mint a separate download KS. No URL, token, body, header
or request hash is serialized into the public result.

GET uses the existing pinned-CA fixed-origin Client, disabled proxies/redirects,
and its independently vetted spawn deadline executor. Response bytes and header
pairs remain in bounded private IPC; raw duplicate headers are not collapsed.
Each GET has a total 30-second deadline; the source flow has a 180-second bound.
The full object is limited to 2 MiB, checked against the original 1,511,134-byte
source hash, then first/last ranges require 206 and exact Content-Range/bytes.

The original 2-second/30-second quiet boundary, finite scanner limits, common-end
checks and original start offsets remain unchanged. A late append fails, not a
privacy waiver. A rejected URL is not a playback pass. Unknown signing semantics,
HLS mapping, decoding and additional fixtures remain separate work.

After independent review, root runs `run_progressive.py --check`, then the same
script with `--output` pointing to a new exclusive artifact directory. The new
stage `/var/lib/kaltura-baseline-short-progressive-r1` must be absent; the exact
previous metadata unit must be inactive. Historical stages are not overwritten.

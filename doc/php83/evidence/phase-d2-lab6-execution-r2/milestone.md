# Actual D2 lab6 success — 2026-09-28

The coordinator deliberately restored the coherent lab-only checkpoint after
preserving the prior contained failure. Current package/configuration identities
and absent failed RUN were verified. No partial dpkg transaction was resumed.

New control-only lab6 artifact keeps the original payload and moves only ES daemon
logs to an exclusive uid112:gid1120700 leaf beneath root-trusted /var/lib. The
private Kaltura log parent was not weakened. Lab5's /var/log proposal was rejected
by actual preflight before APT. Lab6's first transaction configured the package,
but a literal-address check rejected native IPv4-mapped loopback output. That
failure remains preserved. A bounded ES-only diagnostic observed exactly the two
mapped loopback sockets, with Java ownership, start/stop and privacy checks passing.

Independently reviewed R3 normalizes only those two observed representations,
retaining full listener-set and Java ownership checks. Eight independent socket
tests passed; the unchanged lab6 artifact has fourteen independent local tests,
two identical builds and an independent archive review. Actual fresh normal APT
with R3 exited 0. The terminal reports all five final checks passed and workers
held. Eight fresh indices, eleven aliases, source-pinned mappings, green health,
ICU, 1GiB heap and disabled GeoIP downloads passed. Native Apache PHP effective
ES/cache configuration passed. Apache, Monit, MariaDB and Elasticsearch are active.

This scoped commit records the accepted executor/socket regression and sanitized
execution/recovery evidence. It does not turn the broader still-local installer
chain or private DEBs into a reproducible release bundle. Historical failures are
not relabeled PASS. Private logs, generated secrets, DB and VM payloads stay local.

Next execution lane: D3 nginx privacy-safe logging design, exact artifact tests
and independent review before its normal APT install; then the server meta-package.
Secret-bearing traffic and worker release remain gated. OpenSpec is still 4/51;
full seed, effective authorization, real media flows and all distro/performance/
recovery/release requirements remain outstanding.

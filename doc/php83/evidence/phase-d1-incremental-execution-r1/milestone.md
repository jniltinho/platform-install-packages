# Actual incremental D1 lab installation — 2026-09-28

Codex coordinator executed the reviewed D1 executor against the owned `.83` lab.
Guard passed, normal offline APT exited 0, and exactly kaltura-batch
18.20.0-1+php83lab3 was added to the previous thirteen-package cohort.
Package, metadata, input-canary and generated-secret checks passed; workers
remain held. A full memory/disk checkpoint was taken before installation,
without claiming a rehearsed application recovery.

Independent Codex review is recorded alongside the execution receipt. This
commit records sanitized actual execution evidence, not the entire still-local
installer implementation/dependency chain or a reproducible release bundle.
Its exact reviewed executor and package identities remain in the contract.

Next: D2 Elasticsearch installation. Its actual read-only guard rejected
CACHE_EXTRA_ENDPOINT before creating RUN or executing APT. Root confirmed one
unrendered @MEMACHED_HOSTNAME_FOR_WRITE@ token in the generated remote cache
write list. The existing base postinst contains an internal-space typo in this
replacement token. A bounded separately reviewed lab correction is being
prepared; the endpoint guard is not being weakened.

No OpenSpec checkbox changed: 4/51 complete, 47 remain. Full seed persistence,
effective authorization, real worker/media flows, all distro/performance/recovery
requirements and final release gates remain open. Production was not touched.

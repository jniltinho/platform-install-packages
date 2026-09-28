# Pilot-only Elasticsearch input authentication

Host-only preparation on 2026-09-28. No guest package source or service changed.
Elasticsearch 7.17.29 amd64 and analysis-icu 7.17.29 were downloaded into
`/tmp/php83-elastic-origin/`; binaries are not committed.

The signing-key fingerprint matches the [official 7.17 Debian instructions](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/deb.html):
`46095ACC8548582C1A2699A9D27D666CD88E42B4`. `gpgv` verified the retained
InRelease, whose SHA256/size authenticated `main/binary-amd64/Packages.gz`.
The exact 7.17.29 package stanza then authenticated the downloaded DEB by
size and SHA256. See `verified-artifacts.json` and retained signature status.

The ICU plugin ZIP matches its official HTTPS SHA512 sidecar; its descriptor
requires exactly Elasticsearch 7.17.29. This checksum is not a separate plugin
signature. [Official plugin instructions](https://www.elastic.co/guide/en/elasticsearch/plugins/7.17/analysis-icu.html)
describe the matching plugin installation; no plugin installer was executed here.

These checks establish input provenance, not package installation, runtime
compatibility, API/search acceptance or current security support. The 7.17
manual explicitly warns that no further bug fixes/documentation updates will
be released. Keeping the existing 7.17 family for this controlled pilot is not
an approval to publish an unsupported stack or silently upgrade Elasticsearch.

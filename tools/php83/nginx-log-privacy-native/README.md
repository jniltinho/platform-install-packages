# Native privacy fixtures (not deployment)

The original negative probe writes synthetic data only. Never substitute live
credentials. `run.py` accepts `--binary` and `--output` (see its argument parser).
`integration.py` expects `/tmp/php83-nginx-native-fixture-bin/nginx`.

External prerequisite: the privately built lab2 package
`kaltura-nginx_1.23.0-1+php83lab2_amd64.deb`, SHA256
`993b5a45e6c3db5488cd98c34fc8ee6634dfbafae98ac3129b8dc17276271519`.
Verify its hash, extract with `dpkg-deb -x` into a newly created disposable
unprivileged directory (do not install), then copy its `opt/kaltura/nginx/sbin/nginx`
into a newly created, user-owned `/tmp/php83-nginx-native-fixture-bin/`.
Do not overwrite an existing path. Verify the binary SHA256 is
`1a995dddd470f013258b1890cfc7c9e3b10c344461eb085de6b2ef8f991faec0`.
If unavailable, record NOT_EXECUTED; do not download a different nginx.

These fixtures use host shared libraries, not a fully pinned container or VM.
The package/binary are deliberately not committed. Thus this directory alone is
not a fresh-clone reproducible installer. Run unprivileged with synthetic inputs
and loopback only. The guardian test checks frozen binary identity but dynamically
records current guardian/sanitizer hashes: compare those to the evidence before
claiming reproduction of a particular revision.

Successful reopen creates a new log and subsequent requests succeed. A reload
signal plus subsequent requests does not by itself prove worker replacement.
The original guardian has an independently reproduced exit-drain defect; passing
four bounded native cases is not complete diagnostic/lifecycle acceptance.

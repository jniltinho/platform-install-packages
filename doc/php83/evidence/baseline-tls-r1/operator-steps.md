# Coordinator-only staging/execution handoff (pending independent review)

Do not run while .74 100-call workload is active. Root alone owns the VM and service transition. No agent in this lane executed SSH/VM/OpenSSL/Apache.

Frozen guest source pair:
- setup.py SHA1666cc30fc01a2114be43c3cf66053d7114481eb76698969fe3bbc8a86b26d39.
- render.py SHA01f790ea2023c6d5990c5344e665d540b98847432bd7e92262f4d7a4b8b8fa9d.

After independent review, root may stage only these public files in new exclusive `/var/lib/kaltura-baseline-tls-code-r1` (root:root0755 directory,root:root0444singlelink files), using reviewed strict .74 transport and exact VM/NAT target guard. Refuse occupied stage; verify local and guest SHA pair before each invocation. Do not use `/var/lib/kaltura-baseline-tls-r1` for code staging: that is the executor's exclusive private state/key/backup directory and must remain absent until --execute.

Bounded default read-only check, from immutable guest code directory:

```
sudo -n /usr/bin/python3 -B /var/lib/kaltura-baseline-tls-code-r1/setup.py
```

Expected TLS_PREFLIGHT_ONLY/exit0. Any metadata/path/module/listener/pin refusal is a stop, not permission to chmod, remove oldstate, disable verification or rerun package hooks. First check does not generate keys or mutate Apache. Root checks source hashes again and preserves public exit/status.

After100 is terminal and exclusive transition approved:

```
sudo -n /usr/bin/python3 -B /var/lib/kaltura-baseline-tls-code-r1/setup.py --execute
```

Use host timeout sufficiently beyond bounded phases (e.g.900s, including possible rollback), capture only closed JSON receipt; never raw private state or stderr. A host transport timeout remains incomplete and requires root recovery check, not automatic retry. Script command subprocesses have individual30/60s bounds and process-group kill on interruption. Private terminal.json is a status-only receipt and may be read by root separately if transport fails; no key/config backup content may be exported.

Expected success LAB_TLS_INSTALLED_TRUSTED_HANDSHAKE_ONLY includes publicCA PEM/DER SHA, TLSversion, correctSAN trust and wrongCArejection, no API/user/HLS acceptance. Keep existing HTTP80 and verify no wildcard443. After success root may separately export only ca.crt publiccertificate bytes to the guarded client with recordedSHA; no CAprivatekey/serverkey/keyhash export or globaltrust installation. Subsequent authenticatedHTTPS requires existing finite privacy scanner to cover both new root0600logs under /var/log/apache2.

Failure receipt retains private keys/logs/backups; rollback removes onlyownedconfig/link and restores pinnedports with Apache restart, then checksactive/noTLSlisteners. rollback_complete=false or lostreceipt means inspect/recover exclusively before otherwork. Do not delete evidence or reuse consumedstate. These steps are a handoff, not execution evidence.

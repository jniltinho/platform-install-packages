# Task 1.2 — current read-only baseline observations

Root executed the frozen `tools/php83/baseline-host-context-r1/collect.py` after
independent Codex source review and four pure test passes. Actual Claude also
independently reviewed and passed the four pure tests (exit0); it did not access
the VM. `actual-readonly.json` records root's real guest collection, exit0:

- Exact VM `9e954729-16f3-4eda-9db5-b94e5ada9e44`, running, 4 CPUs/8192 MiB.
- Guest `kaltura-php74-baseline`, address `.74`, CLI PHP 7.4.33.
- Public package/module/source-subset identities only; no credential reads,
  SQL, HTTP requests, worker release, upload or guest writes.

Command: `python3 -B tools/php83/baseline-host-context-r1/collect.py --output doc/php83/evidence/baseline-host-context-r1/actual-readonly.json`.
Pure tests: `python3 -B -m unittest discover -s tools/php83/baseline-host-context-r1 -v`.
Output creation is exclusive; choose a new file for repetitions. This frozen
collector uses the original local SSH configuration and must not be confused
with the subsequently hardened transport described below.

## Supplemental host evidence

`environment-observation.json` was obtained with read-only `VBoxManage
showvminfo <exact-vm-uuid> --machinereadable`, the exact attached ImageUUID,
`VBoxManage showmediuminfo disk <exact-image-uuid>`, and that VM's Vagrant
box_meta file. It records IntelAhci, dynamic VMDK and 65536 MiB capacity, with
box metadata bento/ubuntu-24.04 version202510.26.0. Unknown original box checksum
and coherent snapshot remain null. An unsupported `showmediuminfo
--machinereadable` attempt failed before the supported plain-output read;
that failed attempt is not evidence of a disk mutation or missing disk.

The original SSH config had host-key checking disabled. Root preserved it and
created a separate mode0600 strict config and known-hosts file after checking
this exact VM's NAT mapping to127.0.0.1:2201. A bounded ed25519 keyscan and strict
hostname probe passed. `ssh-transport.json` records public hashes and the TOFU
limitation: the key was observed on the checked local VM port, not independently
provisioned out of band. Future native execution uses the strict config.
No private key was read, exported or changed; public host-key material stays
outside the repository.

These observations do not freeze the full protocol or close1.2/5.5. Web runtime,
complete installed source/config, profile/typed fixture, box checksum/recovery,
trusted HTTPS/HLS/long-media/worker behavior and repeated timings remain pending.
The baseline includes the previously approved privacy overlay; it is not labeled
published-intact. Production `.20` and candidate `.83` were not accessed here.

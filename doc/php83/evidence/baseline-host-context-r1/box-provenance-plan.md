# Bento origin: bounded read-only provenance inspection

Outcome: both VM records name the same cached Bento version/provider/architecture, but the original `.box` SHA256 remains **unknown**. No VM action, large download, install, credential read or broad home scan occurred.

## Local joins observed

- Baseline Vagrant id:9e954729-16f3-4eda-9db5-b94e5ada9e44.
- Candidate Vagrant id:33f4f25f-1cf2-4cc5-90ff-d519c29b2aee.
- Both project `box_meta` files are byte-identical SHA53d40c263eaf75948b65fdcbb24dda1fbf30511fae0c1d3b89fe00d564899362: name bento/ubuntu-24.04,version202510.26.0,provider virtualbox,directory boxes/bento-VAGRANTSLASH-ubuntu-24.04/202510.26.0/amd64/virtualbox.
- Narrow cache directory `/home/nilton/.vagrant.d/boxes/bento-VAGRANTSLASH-ubuntu-24.04/202510.26.0/amd64/virtualbox` contains extracted VMDK,box.ovf,Vagrantfile,metadata.json and bookkeeping, not an original `.box` archive. metadata.json explicitly says architecture amd64/provider virtualbox, SHAe736a4f2813679dc974566957c677d4cc8e64f02251243b71e829c3707da0a0a.
- Cache parent metadata_url points to the official endpoint below, SHA177d3402fc7f7a9ce7c5f76ae3e0198fe722aed2d05466b83a252f2c8611b84e. Cached box.ovf SHA77ff68534dcc512a52ecabba77fad970d876cdf8b3a843194965c6c50e512bc7; cached Vagrantfile SHAc460ea810dcaa59eb318763dc63ded5ce3525571b80aa14c4de8de86c6b3d89a. These are current cache identities, not upstream attestations or hashes of installed VM disks.

## Official metadata observation

On2026-09-28 a bounded HTTPS GET of [Bento Vagrant metadata](https://vagrantcloud.com/api/v2/vagrant/bento/ubuntu-24.04) returned11495bytes. Browser fetch failed; Python urllib succeeded with20s timeout/2MiB response cap. Exact version202510.26.0/provider virtualbox/architecture amd64 has `checksum_type:"none"`, `checksum:""`; status active. Its named archive endpoint is `https://vagrantcloud.com/bento/boxes/ubuntu-24.04/versions/202510.26.0/providers/virtualbox/amd64/vagrant.box`. No archive bytes were downloaded. Current upstream metadata therefore does not supply the missing checksum. No claim that metadata has remained unchanged since initial import.

## Consequence / smallest next action

Keep original_box_sha256=null. Matching Vagrant/cache labels support same declared origin, not cryptographic original-box equality, current-disk equality, or complete environment freeze. Hashing the extracted VMDK or retarring the cache would produce a new identity and must not be relabeled the downloaded archive hash. Prefer any operator-retained original archive plus contemporaneous download/checksum receipt. If absent, a separately authorized future download can establish a *newly obtained* archive identity and compare extracted members to this cache; it still does not retrospectively prove which bytes originally provisioned either VM. Do not change protocol or unknown-state acceptance silently to close this gap. Runtime/read-only fixture observations can continue under their own explicit non-freeze scope.

## Authorized subsequent download (new evidence, not retrospective proof)

Root authorized the bounded official download after this report. HEAD returned651326766bytes through HTTPS public-address-resolved Vagrant→Hashicorp API→S3 redirects;169GBfree. Download was exclusive under sibling artifacts/baseline-box-origin-r1, max2GiB/600seconds with outer610seconds, proxies disabled and no credential headers. New archive SHA256 **14ae82e423c270d1c03907faf90691b0fbd673b16bfc369a949808e4e6991b82**,651326766bytes. No installation or VM change.

Initial comparison rejected the archive's numeric top-level directory (exit1); retained as failure. A separate comparator pinned the new full archive and allowed exactly its observed15076530450 prefix plus four expected regular files. No symlinks/traversal/extraction/embedded execution. Subsequent comparison exit0: all four tar-member bytes match existing cache files, including660467712-byte VMDK SHAd5fb31ae860c0d8ed68f04461e1dea5348b6a46c885158e0a3de52f0108f31b5. Public receipt box-new-download.json; source download/comparison scripts retained in the artifact directory.

This now pins a NEWLY_DOWNLOADED official archive with an exact cached-member match. It strengthens common cached origin correspondence, but does not prove historical provisioning or equate current changed VM disks with the base image. Keep those claims false; do not silently replace historical_box_sha256=null with a historical-provenance assertion.

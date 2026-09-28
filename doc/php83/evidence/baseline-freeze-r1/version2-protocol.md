# V2 explicit current-selection observation

Coordinator authorized the narrow correction after actual R2 partial observation.
This is not an application or task waiver. Frozen V1 remains unchanged: its
positive-only historical entry version assumption was not required by Decision7
or native API semantics. Source rationale and pins are recorded in
version-profile-next-delta.md and version-profile-source-pins.json.

New files end in `_v2.py`, except root host `run_v3.py` (capture revision 3).
After independent review, coordinator commands are:

```
python3 -B tools/php83/baseline-freeze-r1/run_v3.py --check
python3 -B tools/php83/baseline-freeze-r1/run_v3.py --output NEW_EXCLUSIVE_LOCAL_DIRECTORY
```

New immutable guest stage `/var/lib/kaltura-baseline-freeze-v2` must be absent;
known previous R2 unit must be inactive. No old stage/file/receipt overwritten.
All original target/network/credential-before-privacy/finite-scan protections
are retained. New guest only changes observation module identity, null-to-empty
SELECT representation, exact previously observed profile14 guard, and fixture
construction independent of positive entry-data version. Native profile object
is KalturaConversionProfile; empty configured flavors are an observed empty list.
No profile creation/change, grant, upload or bootstrap is introduced.

V2 fixture has explicit `media_get_version:-1`, readonly observed entry-data
version (zero or null permitted), separate source asset/FileSync identity, typed
media projection and native typed list count. Fixed media.get selection means
current/default for this exact owned entry, not a claim of historical-version
coverage. Empty native data returns zero; unsupported representation stays null.
`protocol_v2.py` retains 34/33/33 and failure accounting/timing behavior. Eleven
focused tests include an actual pure fake-transport 100-call run with all 33
media.get requests using -1; this is not native benchmark execution.

Assembler V2 accepts only the V2 shape and still emits approved_freeze=false,
full_acceptance=false and recovery_snapshot_attested=false. Source asset version
2 is never substituted for entry-data version. Current web PHP runtime,
environment/recovery approvals, long-media and repeated timed flows remain open.

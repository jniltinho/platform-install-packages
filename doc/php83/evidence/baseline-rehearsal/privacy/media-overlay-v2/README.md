# Media replay V2 — functional partial success, privacy failure

Actual Codex native replay in lab74 only. Guest exit 2 (launcher exit 0 is not
acceptance); cleanup inactive, stderr empty. Synthetic entry `0_r6b8sm7t`,
partner 102, reached READY after 24 polls; original asset `0_2qiu0fp0`, version 2,
FileSync 306. Source/store/HTTP bytes share SHA256
`612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473`.
Owned filtered media.list passed. This is not HLS/TLS/benchmark/full acceptance.

Unlike V1's preserved indeterminate Incomplete, both V2 scanners completed.
Final file-window counts `[0,0,3,3]` mean secret/full-prefix zero, **exact full KS
and its prefix each found three times**. Journal counts zero; three new records.
The final gate rejected `PRIVATE_MARKER_LOGGED`; no more auth/uploads followed.

Private bounded read used original boundary-3 inode/device/start offsets and
published final cutoffs; no historical scan from zero. Locator output contains
only static source literals/keywords, file metadata and counts—never log lines,
KS, credentials or secret hashes. The three same-candidate occurrences in
kaltura_api_v3.log at relative lines 621/625/1102 are SQL INSERT/UPDATE involving
entry CUSTOM_DATA. `private-window-keywords.json` is categorical evidence.
Candidate-identification frequency is supporting evidence, not a reconstruction
of the expired request's private ephemeral KS.

Current logMethod shows the stream writer because the overlay added a stack
frame; caller attribution repair is tracked independently in caller-frame-v1.
Core KalturaStatement.execute expands binds then logs the SQL at line 61.
Direct PDO also logs raw SQL, but no assertion that all three observations came
from it. Source-path confirmation and prepared-display repair are in
sql-display-v1; no new application correction installed yet.

Claude preparation review executed 24 local tests and verified 11 frozen hashes.
It is not an independent native replay. V1 remains indeterminate, not relabeled
as this later proven leak. Both uploaded lab fixtures remain retained.

## Correction after narrower SQL projection
The earlier entry/CUSTOM_DATA/UPDATE description was based on substrings and
was over-specific. `private-sql-shape.json` plus
`private-sql-table-source.json` identify all three as **INSERT INTO track_entry**;
source table literals independently match BaseTrackEntryPeer and its map.
BaseTrackEntryPeer.doInsert829/853 invokes BasePeer's prepare/bind/execute path.
The raw source line/KS remains guest-private. This corrects attribution, not the
recorded full-KS occurrence count or the original scanner outcome.

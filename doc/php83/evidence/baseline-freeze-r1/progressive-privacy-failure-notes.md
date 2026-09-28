# Progressive443 privacy failure: retained, not waived

The ended native run completed original-byte and range checks, but its final
status is FAILED_OBSERVATION / PRIVATE_MARKER_LOGGED at BATCH_PRIVACY. This is not
an accepted delivery/privacy run. The old source and receipt remain unchanged.

## What can be recovered

Boundary files contain start inode/offset maps and private journal cursor, not
patterns or matched counts. Scanner failure files represent scanner incompleteness,
not accepted()'s positive match. The guest failure stdout contained a last scan
observation, but the host's deliberately closed projection omitted it and raw
stdout was not persisted. Thus the exact old ephemeral KS and original index map
cannot be reconstructed from the boundaries. Passing the earlier secret/KS-only
scan does not rule out a later credential append.

The reviewed read-only diagnostic only classifies route-shaped tokens in the
saved file windows, privately. It exports category counters, never source text,
URLs, filenames, credentials, hashes or cursors. It cannot retrospectively turn the
failed run into a privacy pass and does not scan the journal.

The creation source used `privacy-media-<32hex>-short360` for the entry name.
Native flavorAsset/kAssetUtils construct a `/fileName/` parameter from the entry
name and optional asset name. The URL helper enrolled every segment >=16 chars.
This supports a testable public-filename hypothesis, not confirmed attribution.

## Required future derivative, before another authenticated run

1. Save a root-only bounded match receipt **before** accepted() can throw. Include
   audit number, closed phase, per-pattern index, count and provenance category.
2. Compute provenance from private exact comparisons, including current-secret
   full/prefix, current-KS full/prefix and explicit URL-candidate full/prefix.
   Never infer credential status from length/charset alone; no needle or hash.
3. Export only fixed category/index/count projections for files versus journal,
   preserving incomplete-scan codes separately. Do not claim per-file attribution
   from the existing scanner's aggregate file counts.
4. Any exemption for a native filename must be limited to authenticated route
   grammar and a privately verified source-derived field identity. Unknown routes,
   signing parameters, query strings and actual credential markers remain blocked.
5. Preserve original start boundaries, token patterns and finite common-end checks;
   no silent reclassification of this historical failed receipt.

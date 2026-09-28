# R2 observation: source-supported next delta (proposal only)

No VM action or source/artifact change in this review. R2's unresolved fields
are not evidence of an application failure. Preserve the successful partial
observation and failed R1 capture separately.

## Version selection

Original `alpha/lib/model/entry.php:1685–1703` returns 0 when entry.data is empty;
otherwise it returns the filename stem of the first `^` segment (or `&`).
`setDesiredVersion` at 1041–1044 merely assigns an in-memory field.
`KalturaEntryService.php:1214–1234` uses -1 as default, only calling that setter
for a non-default version. Entry API `version` is the readonly entry-data version,
not flavor asset.version. The five-field projection used by the benchmark does
not even contain that version property. Matching projections for arbitrary
requested versions therefore would not prove an existing historical version.

`baseline-api/protocol.py:67` requires entry_version >=1. Decision 7 requires a
frozen reproducible authenticated media.get workload, not a positive historical
entry-data version. The positive restriction is a helper assumption, not a
native API prerequisite. Do not invent a positive entry version from asset 2 or
issue get(1) merely to make that helper accept it.

Proposed separately reviewed versioned protocol: freeze explicit default-current
selection (-1) for the exact owned entry, preserving the 34/33/33 call mix,
projection types and list pagination. Record observed entry-data version 0 or
unknown separately from source asset version 2 and current-source identity.
This requires a NEW protocol/fixture revision, not silently editing the frozen
8-key V1 protocol. Independent review and coordinator approval precede use.

## Profile observation defect

`ConversionProfileService.php:151–161` returns **KalturaConversionProfile**.
The physical model is conversionProfile2; our observation.py incorrectly expects
API objectType KalturaConversionProfile2. Thus UNRESOLVED_API_PROFILE does not
prove profile 14 inaccessible or absent. Correct only in a new reviewed observer
revision, retaining any genuine API exception as unresolved (no admin session).

The API maps conversionProfileId to entry.getConversionQuality (custom data).
entry.php:1847–1856 setter writes BOTH the physical conversion_profile_id and
custom-data conversion_quality; they should not be conflated without observing
the API field or a safely decoded comparison. Physical profile 14 is a stored
selection observation, not yet the complete API relationship proof.

## Proposed bounded root-owned read-only SQL diagnostics

Use the previously reviewed private DB socket transport, a read-only transaction
and finite timeout. These literal SELECTs expose no entry.data/custom_data,
profile names, URLs or credentials. Validate cardinality and types before export.
No API/admin session, source bootstrap, grants, profile changes or upload replay.

```sql
SELECT id,partner_id,conversion_profile_id,
       data IS NULL AS data_null,
       COALESCE(data,'')='' AS data_empty,
       OCTET_LENGTH(COALESCE(data,''))<=256 AS data_within_bound,
       COALESCE(data,'') REGEXP '^[0-9]+([.][A-Za-z0-9]+)?$' AS simple_numeric_stem,
       LOCATE('^',COALESCE(data,''))>0 AS has_caret,
       LOCATE('&',COALESCE(data,''))>0 AS has_ampersand
FROM entry WHERE id='0_wzmt2sfy' AND partner_id=102 LIMIT 2;

SELECT id,partner_id,status,type
FROM conversion_profile_2 WHERE id=14 LIMIT 2;

SELECT conversion_profile_id,flavor_params_id
FROM flavor_params_conversion_profile WHERE conversion_profile_id=14
ORDER BY id LIMIT 129;
```

First and second queries require exactly one row; profile partner must be 102 or
0; third is capped at 128 accepted rows plus one overflow sentinel. Export only
known entry ID, numeric profile/partner/status/type/flavor IDs and closed shape
booleans. A null/empty entry.data confirms native zero behavior; non-simple data
remains unknown without another source-justified parser, never raw export.

A revised read-only observer should also retain the already validated media
projection and native typed list count when no positive V1 fixture exists. R2's
reduced public projection omitted those useful fields. This is an observation
schema correction, not a workload or application mutation.

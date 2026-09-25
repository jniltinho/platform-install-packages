# Claude independent review — dependency attribution follow-up

Local-only review. No VM, network, git, PHP execution or package installation.
Structured record: [claude-review.json](claude-review.json).

## Inputs (unchanged before and after the review)

| Input | SHA-256 |
|---|---|
| `/tmp/kaltura-php83-audit/Rigel-18.20.0.zip` | `58d534d0…b0ab28` |
| `build.py` | `25eff8fa…0833ba` |
| `primary.json` | `232ad945…43ec2` |
| `doc/php83/dependency-attribution-followup.md` | `8779b059…f60` |

These hashes match `review-inputs.json`.

## Executed checks

| Check | Exit | Result |
|---|---|---|
| `python3 build.py --output claude-rebuild.json` | 0 | summary 20/12/14/0/15/2/4999, stderr empty |
| `cmp primary.json claude-rebuild.json` | 0 | byte-identical |
| Separate inline `zipfile` verifier (does not use `build.py`) | 0 | 39 cited sources: hash, byte count, line count and every excerpt match; 20 row manifests recomputed with no mismatch |
| ZIP SHA-256 after the run | 0 | unchanged |

## Disputed labels (checked against ZIP bytes)

- **Google `-1.1.2` → LIBVER 1.1.5**: confirmed (`src/Google/Client.php` L28). It is the only LIBVER in either Google tree.
- **Facebook not MIT**: confirmed. The L1-23 grant covers use "in connection with the web services and APIs provided by Facebook". SDK `VERSION` is 5.0.0 (L60); Graph `v7.0` (L65) is a separate constant.
- **LGPL ambiguity**: confirmed. Propel (L18) and tFPDF (L8) say "LGPL" without a version. HTMLPurifier and NuSOAP grant 2.1 or later. The PHPMailer header has no version, and its bundled text is LGPL 2.1.
- **Symfony license missing**: confirmed. The top level holds only `VERSION` and `symfony.php`. The only license file nested inside is `vendor/propel-generator/LICENSE` (LGPL 2.1). `symfony-data` has no license file.
- **Composer 15 vs 2**: confirmed. Only `flix-tech/confluent-schema-registry-api` 4.0.0 (`d014797d…`, MIT) and `wikimedia/avro` v1.9.0 (`b2e0c9d7…`, Apache-2.0) have files. The only top-level Avro directories are `composer`, `flix-tech` and `wikimedia`.
- The other version and license labels match their excerpts. As intended, all 20 rows stay incomplete. No waiver is granted.

## Discrepancies

1. **D1 (medium), doc L14-15**: the doc says "a canonical … manifest hash" and that "All 4,999 files … contribute to those identity manifests". In fact there are only 20 per-directory manifests, covering 4,997 files. `vendor/.project` and `vendor/.buildpath` are counted in `vendor_files=4999` but appear in no manifest.
2. **D2 (low), doc L50/L80**: the legacy Google version is marked unresolved, but an in-tree candidate is not cited. `src/io/Google_HttpRequest.php` L27 (`e17064f3…f144a6`, 7,776 B) has `USER_AGENT_SUFFIX = "google-api-php-client/0.6.5"`. It should be cited as an unadjudicated literal. It does not prove the release version.
3. **D3 (low), doc L35-36**: "unrelated nested Propel generator license" should read "nested, separately scoped". The code is bundled inside the Symfony tree, so it is not unrelated.

Minor: `build.py` silently clips excerpt ranges that run past EOF (Zend LICENSE 1-32 → 1-27, EventDispatcher 1-20 → 1-19). The recorded ends are correct.

## Limitations

- No upstream sources were consulted, and no legal conclusion is made.
- The rebuild reuses the author's builder. Independence comes from the separate verifier and a manual reading of the excerpts.
- The search for missed evidence used filenames and regex, so it is not exhaustive.
- Out of scope: package-only overlays, non-vendor dependencies and reachability.

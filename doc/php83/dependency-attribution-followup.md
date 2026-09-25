# Bundled dependency attribution follow-up — original Rigel ZIP

This is a **bounded metadata attribution delta**, not completed task 1.1/5.4,
T0-04, a transitive SBOM, legal compliance approval or PHP 8.3 compatibility.
The original inventory ledger is unchanged. Its 20 unresolved vendor rows now
have individual follow-up records; none is silently marked fully attributed.

## Inputs and method

Original archive SHA-256:
`58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
[Primary report](evidence/dependency-attribution-followup/primary.json) records
exact ZIP-member SHA-256, byte count and line-numbered excerpts for every cited
file, plus per-directory file counts and a canonical path/hash/size manifest hash.
The 20 directory manifests cover **4,997** files; two vendor-root IDE files
(`vendor/.project`, `vendor/.buildpath`) are outside those manifests. Their exact
hashes are added in [review corrections](evidence/dependency-attribution-followup/review-corrections.json),
reconciling all **4,999** vendor files. Reading
literal version/license notices is not structural code analysis; no graph-based
conclusion or PHP execution was performed. Input ZIP is verified before/after.
No external source or inferred present-day license replaces a bundled notice.

Memory retrieval was performed first (global lookup, then explicit
`default/platform-install-packages-php83` lookup). Hits did not establish a
completed attribution. Current ledger and ZIP bytes are authoritative here.

## Concrete delta

- **12 of 20** directory rows have an exact version declaration in a cited file;
  the MaxMind declaration applies only to GeoIP2, not its separate Db reader.
- **14 of 20** have some scoped license evidence, including mixed/partial notices;
  this is not 14 complete package-license decisions.
- **0 of 20** are claimed completely attributed across every nested file and
  upstream revision. Every row retains explicit remaining work.
- The Google directory ending `1.1.2` actually declares **LIBVER 1.1.5**.
- Facebook declares **SDK 5.0.0**; its Graph API `v7.0` is not an SDK version.
  Its specific Facebook-services permission is not relabeled MIT.
- Symfony declares **1.0.1**. Its referenced top-level license is not supplied
  by the separately scoped nested Propel generator license. `symfony-data` does not
  acquire a proven release or license just from neighboring Symfony files.

| Directory | Exact scoped version declaration | License evidence (scope, not blanket approval) |
|---|---|---|
| `vendor/IP2Location/` | Unresolved | Database README: GENERAL PUBLIC LICENSE, June 1991 |
| `vendor/MaxMind/` | GeoIP2 v2.4.5 | Unresolved |
| `vendor/PHPMailer/` | 5.2.1 | LGPL declaration; bundled license text version 2.1 |
| `vendor/ZendFramework/` | 1.9.6 | New BSD declaration; bundled three-condition redistribution text |
| `vendor/akamai/` | Unresolved | Unresolved |
| `vendor/avro/` | Unresolved | See separate Composer metadata records and exact bundled license texts |
| `vendor/aws/` | 2.7.21 | Apache License 2.0 bundled root text |
| `vendor/facebook-sdk-php-v5-customized/` | 5.0.0 | Facebook-specific permission limited to Facebook web services/APIs; retained notice |
| `vendor/fpdf/` | 1.7 | Bundled permissive use/copy/modify/distribute/sublicense/sell permission text; no SPDX inferred |
| `vendor/google-api-php-client/` | Unresolved | Apache License 2.0 explicit source header |
| `vendor/google-api-php-client-1.1.2/` | 1.1.5 | Apache License 2.0 explicit source header |
| `vendor/htmlpurifier/` | 4.6.0 | LGPL version 2.1 or later explicitly granted in source header |
| `vendor/mantis/` | Unresolved | Unresolved |
| `vendor/nusoap/` | 0.9.5 | LGPL version 2.1 or later explicit header |
| `vendor/phpGangsta/` | Unresolved | BSD License label/link; clause variant not established |
| `vendor/propel/` | 1.4.2 | LGPL label without version in inspected header |
| `vendor/symfony/` | 1.0.1 | Unresolved |
| `vendor/symfony-data/` | Unresolved | Unresolved |
| `vendor/tfpdf/` | 1.25 | LGPL label without version in tFPDF header |
| `vendor/webex/` | Unresolved | Unresolved |

### Avro metadata is not an installed-package census

`vendor/avro/composer/installed.json` declares **15** named packages with versions,
source references and license labels. Only **2** expected name-prefixes actually
contain files in this ZIP: `flix-tech/confluent-schema-registry-api` **4.0.0**
(reference `d014797d332107d311c3afac1a6dc6f30988d032`, MIT declaration) and
`wikimedia/avro` **v1.9.0** (reference
`b2e0c9d750da03d95ba979215397f62a6121ddea`, Apache-2.0 declaration).
These are recorded metadata claims, **not verified upstream commit-to-byte
identity**. The other 13 named-prefix absences do not prove absence of equivalent
or relocated code elsewhere. Do not count metadata-only entries as installed.
The Wikimedia license file also contains notices for other implementations;
notice inclusion alone does not prove those implementations are bundled.

### Important remaining attribution gaps

- Package commit/release-to-byte comparisons and local modifications remain
  unverified for all components; per-file SVN/CVS IDs are not package revisions.
- Legacy Google client whole-release version (its HTTP client declares a
  `google-api-php-client/0.6.5` user-agent suffix at line 27, now recorded in
  review-corrections.json), MaxMind Db version/licenses, Akamai license,
  mantis wrapper provenance, phpGangsta version/BSD variant, Symfony and
  symfony-data rights, Webex provenance remain unresolved or partial.
- Propel/tFPDF say LGPL without establishing a version in the cited headers.
  Fonts, nested Symfony vendors, AWS dependencies and Avro metadata-only packages
  need their own scoped attribution. Root Kaltura license is not inherited blindly.
- This does not inspect the 1,670 package-only PHP overlays, non-vendor embedded
  dependencies, executable entrypoint reachability or redistribution obligations.

## Reproduce / review

```sh
python3 doc/php83/evidence/dependency-attribution-followup/build.py \
  --output /tmp/dependency-attribution-followup-new.json
cmp doc/php83/evidence/dependency-attribution-followup/primary.json \
  /tmp/dependency-attribution-followup-new.json
```

Output paths must be new. The builder reads trusted local ZIP bytes without
extraction, downloads, application imports, package installation or VM access.
It is not a hostile ZIP resource-limit verifier.

Independent actual Claude CLI **exit 0**: fresh rebuild and byte comparison exit 0;
a separate inline ZIP verifier checked all 39 cited sources/excerpts and 20
identity manifests. [Review](evidence/dependency-attribution-followup/claude-review.md)
found three real corrections: two unmanifested vendor-root files, an omitted
legacy Google user-agent literal, and overly strong wording about nested Propel.
All are preserved and addressed in the additive correction report and this doc.
The initial report/builder remain unchanged for exact review reproduction; the
reviewed doc snapshot is preserved as `reviewed-doc.md`. Corrections were checked
by Codex directly against ZIP bytes; no second independent review is claimed.
Current tool calls/results and public CLI conclusion are retained in a sanitized
stream; raw hook history and thinking are not repository evidence.

## Parent task mapping

Original **1.1 / T0-04**: supplies exact declared versions and scoped license
notices for the 20 historical directory rows; full inventory remains open.
Original **5.4 / T0-04**: supplies part of dependency/license inventory; active
packaging overlays, generated clients, web/CLI/cron/install/plugin entrypoints,
analyzer pins and every static finding classification remain separate. This is
not permission to redistribute or completion of license/release gates. The
parent should keep these tasks open and link this delta rather than alter the
historical ledger's unknowns or count this as 20 resolved packages.

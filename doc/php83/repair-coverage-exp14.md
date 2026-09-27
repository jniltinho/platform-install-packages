# Exp14 finite repair-coverage reconciliation

Status: **identity join complete; semantic closure assessment remains bounded**.
No task checkbox changed. This is a read-only reconciliation of retained executions,
not another compiler, VM, application or release run.

## Exact denominator and reproduced local checks

The [selected manifest](evidence/exp14-candidate/selected-r1/manifest.json) has
**76 unique paths**, not 76 independent behavior suites. The selected ZIP is
`459feaf9caf2abe55963dce0cac51b8b593e4ff1b46d2eaf9cb7d5c3f13f62a1`.
The [machine ledger](evidence/repair-coverage-exp14/ledger-r2.json) pins the manifest,
every ordered patch, every original/final source hash and all named evidence
inputs. Its [join program](evidence/repair-coverage-exp14/join.py) verifies the
original ZIP member bytes (or verified absence for the new helper), selected ZIP
member bytes, patch bytes, all 76 accepted compiler records within the
retained 11,785-file current corpus, and 43 exact paired-token proofs.
It creates its output exclusively. Run ordinary Python, never `python -O`:

```sh
python3 doc/php83/evidence/repair-coverage-exp14/join.py \
  --output /tmp/repair-coverage-exp14-independent.json
cmp doc/php83/evidence/repair-coverage-exp14/ledger-r2.json \
  /tmp/repair-coverage-exp14-independent.json
```

Choose a fresh output filename if it already exists. These commands read local
archives and retained reports only; no SSH, source extraction, PHP process or
compiler rerun. The initial narrower ledger and its exact `join-initial.py`
remain preserved; r2 adds raw original-archive verification and an explicit fresh
output option. Input and current join-script hashes are embedded in the report.

The narrow automatic loaded-map join finds **25 selected hashes and 16 original
hashes** in 19 named primary reports. The remaining 51 selected hashes are
**not evidence of untested files**: older harnesses often identify source through
stage snapshots or named slots instead of a `loaded` dictionary. This mechanical
join deliberately does not turn a class load into changed-method execution.
`semantic_acceptance_rows: 0` means that this script grants no acceptance; it
**does not mean zero existing behavioral proofs**. The human reconciliation below
is authoritative about the scope of each retained corpus.

## Task criteria, not invented release prerequisites

- **1.6:** minimal confirmed-failure repairs, focused before/after 7.4/8.3 evidence,
  reproducible separate ZIP, preserved original and ordered identities.
- **T1-01 / 5.7:** focused cases for each selected repair, combined manifest,
  controls, behavior/diagnostics and exact/reproducible construction.
- Two real builds and independent artifact verification are already retained in
  [exp14 candidate](exp14-candidate.md). Actual OpenCode primary plus Codex
  independent compiler repetition is complete in [exp14 syntax](exp14-syntax.md).
  Historical runtime README statements that compiler was denied describe an
  earlier phase, not the later authorized compiler result.
- Actual artifact [API4/CLI48 comparison](evidence/exp14-runtime/comparison-r1.json)
  already supplies combined-manifest evidence: 44 positive CLI rows, four expected
  original83 failures, 20 typed baseline comparisons and zero parsed current API
  diagnostic groups. Raw API stderr remains **UNCOMPARED**, not certified secret-free.
- Full AIO, benchmarks, packaging, distro providers and production rollout are
  separate tasks, not new prerequisites invented for closing 1.6. Conversely,
  seven compiler rejections and privacy failures are not waived by closing a
  narrower repair-program task.

## Behavioral evidence by coherent repair family

| Family | Targets | Executed contract and executor attribution | Intentional difference / remaining boundary |
|---|---:|---|---|
| JSON/date/doc-comment | 5 | Actual extracted CLI corpora, original74/current83 comparisons; latest actual OpenCode repeat API4/CLI48. | JSON original83 compilation failures are controls, not positives. |
| Criteria cumulative | 1 | Original alias cases, native return iterator/state cases, cumulative native83 four-process proof and independent Cursor repetition; selected artifact focused corpus. | Class-scoped dynamic-property exemption extends to descendants; strict cross-engine serialized-byte gate remains failed. |
| Null-input | 4 | exp5 actual-class cases and real PermissionPeer SQL dependency cases, then combined API corpus. | Explicit null handling, not casts of arbitrary inputs; see exp5 case inventory. |
| Reflection | 1 | Native resolver and real metadata corpora, followed by exp6 artifact/API integration. | Unsupported forms/errors retained; same-runtime cache proof is not cross-engine serialized-byte equality. |
| Zend_Config | 1 | Six native-return declarations, actual-class original74/original83/candidate83 cases; exp7 integration. | Whole candidate is PHP8.3-only; no candidate74 support promise. |
| Statement native bool | 1 | Actual PDO SQL and selected KalturaPDO/bootstrap corpus, independently repeated; later SQL composition. | Intentional null-to-bool propagation is explicit, not baseline-equality normalization. |
| Curly offsets | 43 | 43 original255/candidate0 controls;153 paired-offset proofs; native74 and83 token purity; actual three-file204 behavior rows and selected artifact68 cases, independent repetitions. | Dedicated behavior corpus covers three files, not all43. The other40 have structural/compile proof; later loads must not be relabeled per-method behavior. |
| Nested ternary | 1 | Full real class147 cases per positive mode,441 rows plus original83 fatal; Claude repeated. | Historical left associativity preserved.130 fixed goldens and17 native74 parity cases are distinct evidence strengths. |
| Autoload | 3 | Real full files/configured task listing,26 process corpus and30 composition processes; actual Claude repeats; selected artifact additions. | Explicit SPL composition differences and expected redeclaration/empty-project failures retained. |
| Pake closure / generator DEBUG | 2 | Real generator consumers,72 selected-artifact generation records plus isolated literal controls; independent repetitions. | DEBUG false becomes integer0 instead of empty argument. No generated application wholesale execution. |
| XML policy | 3 | Actual exp13 artifact40 native83 processes, independent Claude exact repetition. | On exp14: NOT_RERUN_SOURCE_JOIN_ONLY; no Apache request-body/full-backend acceptance. |
| AWS serialization/cache | 4 | Actual exp13 artifact88 native83 processes, independent Claude repetition; historical74 contract separately retained. | Original readers reject new O format; rollback_compatible false. exp14 unchanged-source join, not88 new runs. |
| Dispatcher | 1 | Full-class state/serialization/reflection original/attribute and native74 controls, independent native83 repeat. | Public dynamic storage preserved; attribute exempts descendants/future dynamic names. Not a global suppression policy. |
| PDO/config/exception family | 5 | Nine declaration/full-class processes, independent authorized repeat; two SQL cohorts91 typed rows each and actual Claude repeat. | Explicit DebugPDO v3 prerequisite and four named side-effect seams. Transaction return-type attributes narrowly preserve int/false; MSSQL/backend integration not claimed. |
| Rank signature | 1 | Four full-class metadata/omission processes, native74/copied83; actual Claude repeat. | Seven-byte default removal; PHP74 default-reflection delta explicit. No positive rank-body/persistence execution claimed. |

## Finite remaining closure question and smallest next work

**Do not rerun 11,785 compiler files or build a new AIO just to fill this join.**
The selected source identities, deterministic construction and combined artifact
regression have evidence already. For curly repairs the official [PHP RFC](https://wiki.php.net/rfc/deprecate_curly_braces_array_access)
and [array manual](https://www.php.net/types.array) establish that the two
notations designate the same array/string offset operation before removal.
This is a language-defined syntax equivalence, not an inference from three
sample files. The 43 native token proofs cover **all153 changed pairs**, each
bound to the targeted offset sniff and original/final hashes; every other token,
including comments, strings, interpolation, expressions and control blocks,
is unchanged. Native compile controls cover all43, while the204 behavioral rows
exercise three real implementations, including retained invalid-offset behavior.

**Assessment:** this complete transformation proof plus focused real behavior and
combined-manifest regression is sufficient for the narrow experimental-repair
objective of1.6. It does not establish that every changed enclosing method was
executed or that every old method works on8.3. General engine changes (for example
invalid-offset diagnostics) remain visible, not attributed to the delimiter edit.
For T1-01, the owner should explicitly record that each curly repair is covered
by its own hash-bound token/compile case plus batch behavioral controls. That is
an evidence interpretation for a semantics-preserving transformation, not43
invented method executions or a waiver of seven unrelated compiler rejections.

If the owner instead requires dynamic invocation at every changed site, the
smallest additional corpus is the uncovered subset of153 offset pairs across
at most40 files: map those pairs to existing real-class/task invocations first,
then add bounded argument fixtures only for unhit sites (reads and writes,
including relevant invalid offsets). Do not fabricate peers to hide dependency
failures. There is no justification for11785 new files, fullAIO or another ZIP
build merely to satisfy that stricter interpretation. This ledger does not claim
that the40 files are absent from all other historical method executions.

Rank has sufficient bounded signature/omission evidence to assess this exact
seven-byte edit, including its intentional74 reflection delta; positive rank
persistence remains a separate functional gap and is not supplied by this repair
proof. Likewise, XML/AWS unchanged-source joins are valid provenance reuse but
must remain labeled NOT_RERUN. Reviewers should accept or reject these explicit
scope boundaries, not demand unrelated release gates or mark all51 tasks complete.

**Coordinator decision:**1.6 is closeable as a bounded experimental-repair
milestone, subject to independent review of this finite join. T1-01 /5.7 remains
open while the owner reviews its literal per-repair execution requirement.
Acceptance of syntax-equivalence proof for1.6 does not assert40 method executions.
Any remaining targeted corpus is the finite uncovered-site set above, not an AIO
or release prerequisite. This author has changed no checkboxes.
No further harness-only test count supplies new behavioral evidence.
The post-exp14 privacy SQL/caller repairs are not members of these76 paths as
selected bytes and must not be silently mixed into this denominator.

## All 76 paths, with exact-hash evidence in the ledger

`A/B` counts below are explicit selected/original loaded-source hash references
found by this narrow join, not numbers of method tests. `T` means exact paired
token evidence; every row separately has accepted current compiler evidence.

| # | Path | Family evidence | A/B | T |
|---:|---|---|---:|---|
| 1 | `alpha/apps/kaltura/lib/Services_JSON.class.php` | [json](exp3-runtime.md) | 0/0 | — |
| 2 | `vendor/ZendFramework/library/Zend/Json/Encoder.php` | [json](exp3-runtime.md) | 0/0 | — |
| 3 | `vendor/ZendFramework/library/Zend/Json/Decoder.php` | [json](exp3-runtime.md) | 0/0 | — |
| 4 | `alpha/apps/kaltura/lib/dateUtils.class.php` | [date](exp3-runtime.md) | 0/0 | — |
| 5 | `api_v3/lib/reflection/KalturaDocCommentParser.php` | [doccomment](exp3-runtime.md) | 0/0 | — |
| 6 | `vendor/propel/util/Criteria.php` | [criteria](criteria-marker.md) | 0/0 | — |
| 7 | `alpha/apps/kaltura/lib/myCustomData.class.php` | [null-input](exp5-null-batch.md) | 0/0 | — |
| 8 | `alpha/lib/model/Partner.php` | [null-input](exp5-null-batch.md) | 0/0 | — |
| 9 | `alpha/lib/model/PermissionPeer.php` | [null-input](exp5-null-batch.md) | 0/0 | — |
| 10 | `infra/log/KalturaLog.php` | [null-input](exp5-null-batch.md) | 0/0 | — |
| 11 | `api_v3/lib/reflection/KalturaActionReflector.php` | [reflection](exp6-reflection-integration.md) | 0/0 | — |
| 12 | `vendor/ZendFramework/library/Zend/Config.php` | [config](exp7-config-integration.md) | 0/0 | — |
| 13 | `alpha/apps/kaltura/lib/db/KalturaStatement.php` | [statement-bool](exp9-pdo-integration.md) | 4/0 | — |
| 14 | `alpha/apps/kaltura/lib/myCaptchaImage.class.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 15 | `alpha/apps/kaltura/lib/s3/S3.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 16 | `alpha/apps/kaltura/lib/storage/urlTokenizers/kAkamaiSecureHDUrlTokenizer.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 17 | `infra/general/S3.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 18 | `vendor/IP2Location/IP2Location.inc.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 19 | `vendor/PHPMailer/extras/htmlfilter.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 20 | `vendor/ZendFramework/library/Zend/View/Helper/Navigation/Sitemap.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 21 | `vendor/google-api-php-client-1.1.2/src/Google/Utils.php` | [curly](curly-offsets.md) | 3/1 | yes |
| 22 | `vendor/google-api-php-client/src/service/Google_Utils.php` | [curly](curly-offsets.md) | 3/1 | yes |
| 23 | `vendor/htmlpurifier/library/HTMLPurifier/ChildDef/Custom.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 24 | `vendor/htmlpurifier/library/HTMLPurifier/Encoder.php` | [curly](curly-offsets.md) | 3/1 | yes |
| 25 | `vendor/htmlpurifier/library/HTMLPurifier/TagTransform/Font.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 26 | `vendor/propel/engine/GeneratorConfig.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 27 | `vendor/propel/engine/database/transform/XmlToAppData.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 28 | `vendor/propel/validator/MatchValidator.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 29 | `vendor/propel/validator/NotMatchValidator.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 30 | `vendor/symfony/controller/sfRouting.class.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 31 | `vendor/symfony/helper/UrlHelper.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 32 | `vendor/symfony/i18n/sfDateFormat.class.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 33 | `vendor/symfony/i18n/sfNumberFormat.class.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 34 | `vendor/symfony/i18n/sfNumberFormatInfo.class.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 35 | `vendor/symfony/util/Spyc.class.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 36 | `vendor/symfony/util/sfFinder.class.php` | [curly](curly-offsets.md) | 9/0 | yes |
| 37 | `vendor/symfony/vendor/creole/drivers/pgsql/PgSQLResultSet.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 38 | `vendor/symfony/vendor/creole/util/sql/SQLStatementExtractor.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 39 | `vendor/symfony/vendor/pake/pakeFinder.class.php` | [curly](curly-offsets.md) | 99/0 | yes |
| 40 | `vendor/symfony/vendor/pake/pakeGetopt.class.php` | [curly](curly-offsets.md) | 99/0 | yes |
| 41 | `vendor/symfony/vendor/pake/pakeYaml.class.php` | [curly](curly-offsets.md) | 99/0 | yes |
| 42 | `vendor/symfony/vendor/phing/Phing.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 43 | `vendor/symfony/vendor/phing/lib/Capsule.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 44 | `vendor/symfony/vendor/phing/system/io/BufferedReader.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 45 | `vendor/symfony/vendor/phing/system/io/UnixFileSystem.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 46 | `vendor/symfony/vendor/phing/system/io/Win32FileSystem.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 47 | `vendor/symfony/vendor/phing/system/util/Properties.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 48 | `vendor/symfony/vendor/phing/tasks/system/CvsPassTask.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 49 | `vendor/symfony/vendor/phing/tasks/system/PropertyTask.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 50 | `vendor/symfony/vendor/phing/types/Path.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 51 | `vendor/symfony/vendor/phing/util/FileUtils.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 52 | `vendor/symfony/vendor/phing/util/PathTokenizer.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 53 | `vendor/symfony/vendor/phing/util/StringHelper.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 54 | `vendor/symfony/vendor/propel-generator/classes/propel/engine/builder/DataModelBuilder.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 55 | `vendor/symfony/vendor/propel-generator/classes/propel/engine/database/transform/XmlToAppData.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 56 | `vendor/symfony/vendor/propel-generator/classes/propel/phing/AbstractPropelDataModelTask.php` | [curly](curly-offsets.md) | 0/0 | yes |
| 57 | `alpha/apps/kaltura/lib/baseObjectUtils.class.php` | [ternary](base-object-ternary.md) | 0/0 | — |
| 58 | `vendor/htmlpurifier/library/HTMLPurifier.autoload.php` | [autoload](autoload83.md) | 11/6 | — |
| 59 | `vendor/symfony-data/bin/symfony.php` | [autoload](autoload83.md) | 18/9 | — |
| 60 | `vendor/symfony/util/sfCore.class.php` | [autoload](autoload83.md) | 6/3 | — |
| 61 | `vendor/symfony/vendor/pake/pakeApp.class.php` | [generator](template-generation.md) | 72/27 | — |
| 62 | `vendor/symfony-data/tasks/sfPakeGenerator.php` | [generator](template-generation.md) | 36/39 | — |
| 63 | `alpha/config/kConf.php` | [xml](exp13-xml.md) | 28/31 | — |
| 64 | `infra/general/kSoapClient.php` | [xml](exp13-xml.md) | 28/28 | — |
| 65 | `infra/general/kXmlEntityLoaderPolicy.php` | [xml](exp13-xml.md) | 28/0 | — |
| 66 | `vendor/aws/Aws/Common/Credentials/Credentials.php` | [aws](exp13-serialization.md) | 41/29 | — |
| 67 | `vendor/aws/Aws/Common/Credentials/NullCredentials.php` | [aws](exp13-serialization.md) | 6/6 | — |
| 68 | `vendor/aws/Aws/Common/Credentials/AbstractCredentialsDecorator.php` | [aws](exp13-serialization.md) | 26/24 | — |
| 69 | `vendor/aws/Doctrine/Common/Cache/FileCache.php` | [aws](exp13-serialization.md) | 8/8 | — |
| 70 | `api_v3/lib/KalturaFrontController.php` | [dispatcher](dispatch-rank.md) | 0/0 | — |
| 71 | `alpha/apps/kaltura/lib/db/KalturaPDO.php` | [return-family](return-contracts-sql.md) | 4/0 | — |
| 72 | `vendor/propel/util/PropelPDO.php` | [return-family](return-contracts-sql.md) | 4/0 | — |
| 73 | `vendor/propel/util/PropelConfiguration.php` | [return-family](return-contracts-sql.md) | 6/8 | — |
| 74 | `api_v3/lib/exceptions/KalturaAPIException.php` | [return-family](return-contracts-sql.md) | 4/6 | — |
| 75 | `vendor/propel/util/DebugPDO.php` | [return-family](return-contracts-sql.md) | 4/0 | — |
| 76 | `api_v3/lib/KalturaEntryService.php` | [rank](rank-signature-repair.md) | 0/0 | — |

# Experimental PHP 8.3 source patches

**Not a complete PHP 8.3 port. Not a deployment package.**

The active series is exactly the ordered `patches` array in `manifest.json`.
Do not glob `*.patch` or include the `held/` directory. The original upstream ZIP
and published PHP 7.4 artifacts are never overwritten.

## exp2: JSON offset syntax only

| Patch | Public source path | Changes |
|---|---|---:|
| 0002 | `alpha/apps/kaltura/lib/Services_JSON.class.php` | 40 offset reads |
| 0003 | `vendor/ZendFramework/library/Zend/Json/Encoder.php` | 7 offset reads |
| 0004 | `vendor/ZendFramework/library/Zend/Json/Decoder.php` | 7 offset reads |

These patches only replace `$string{offset}` with `$string[offset]`; algorithms,
masks, constructor behavior and JSON fallback selection are unchanged. They are
local compatibility edits, not an upstream dependency upgrade. The file-level
license/copyright headers remain unchanged (Services_JSON's redistribution
notice and Zend's New BSD notice). A full dependency/license audit remains open.

`held/Registry-cast.patch` is intentionally **not included**. A narrow fixture
passed, but adding dynamic-property writes under ArrayObject flags 2 and 3
changed the PHP 8.3 result relative to unpatched PHP 7.4. Neither its earlier
review nor a passing narrow test authorizes shipping it. `parent::offsetExists`
was also rejected because it changes STD_PROP_LIST behavior.

## Build

Requires Python 3 and GNU patch. No network, Composer or package installation is
performed by the builder. The output directory must not already exist.

```sh
python3 tools/php83/build-experimental-zip.py /path/Rigel-18.20.0.zip /path/new-output-directory
```

The builder checks the upstream archive, every patch, and each changed input /
output hash. Patch offsets/fuzz, mismatches, duplicate ZIP members, traversal and
source symlinks are rejected. ZIP ordering, timestamps and modes are normalized;
file bytes outside the explicit patch series are retained. It includes only the
public upstream archive plus experimental patch metadata, never a configured VM
or live installation. Archive compression reproducibility is checked with the
recorded Python/zlib toolchain; cross-version compression identity is not assumed.

See [experiment evidence and limitations](../../doc/php83/experimental-zip.md).

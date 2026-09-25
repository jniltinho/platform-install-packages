# Registry investigation with Claude CLI

Date: 2026-09-25. No Registry patch promoted to the experimental ZIP.

Two concrete repair requests were sent to the Claude CLI with source and
observed baseline output. Responses are saved under
`evidence/registry-investigation/`. They are advisory: experiments determine
outcomes, and suggested behavioral waivers were not accepted automatically.

## Root cause narrowed by runtime probes

The difference is visible with **native ArrayObject**, not only Zend_Registry.
For flags ARRAY_AS_PROPS (2) and ARRAY_AS_PROPS|STD_PROP_LIST (3):

| Write form | Tested PHP7.4.33 | Tested PHP8.3.6 |
| --- | --- | --- |
| Literal `$object->dynamicProbe = ...` | real object property | array offset |
| Variable `$object->$key = ...` | array offset | array offset |

The same distinction was observed when writing the existing `initial` name.
Both initial and already-read objects were tested. Standard and minimal INI
outputs match within each runtime. Flags 0/1 and Registry were also recorded.
This is evidence about the exact lab runtimes, not a universal statement about
every PHP7.4 build. The diagnostic captures getArrayCopy, public properties and
array casts; it does not imply all magic-method interactions are covered.

`registry-storage.php` now records these write forms explicitly. Earlier
reasoning that treated all property writes alike was too broad. Claude's first
response correctly identified write routing as a candidate cause. Parts of the
follow-up response (including blanket equivalence of getArrayCopy and behavior
of existing-key writes) are not supported by the recorded cases.

## Two attempted repair paths

1. Existing cast-only patch (`Registry-cast.patch`): preserves the full 7.4
   fixture, removes the PHP8 object-argument fatal, but still differs for the
   literal-property cases under flags 2/3. The strict parity failure remains.
2. New `Registry-properties.patch`: cast plus `__set` temporarily clearing
   ARRAY_AS_PROPS. **Rejected.** It changes the 7.4 baseline and does not repair
   the 8.3 divergence. The patch/hash and failure report are retained only as
   a rejected experiment; it must not be applied via wildcard discovery.

No global flag changes, stack-trace heuristics or broad replacement of
ArrayObject were introduced. No diagnostic was suppressed.

## Actual bootstrap container API

Source inspection found `Zend_Application_Bootstrap_BootstrapAbstract` creates a
Registry container and uses **variable-name** property writes at lines 667/681.
Its hasResource/getResource methods use property access. The ActionStack plugin
retrieves the singleton and writes array offsets. These are positive bounded
findings, not an exhaustive alias/subclass audit.

`registry-bootstrap.php` subclasses the actual bootstrap abstract class only
to bypass application construction and forbid run(). It exercises inherited
getContainer/hasResource/getResource with text, zero, false, null, nested arrays,
unset and missing names. Resource values are written using the same variable-
property syntax; resource plugins and full bootstrap initialization do not run.
Existence results, including null behavior, are compared to the actual baseline
rather than assumed from generic isset semantics.

With the **cast-only** candidate, all four differential comparisons pass:
7.4/8.3 with standard/minimal INI. This demonstrates compatibility of these
specific public container operations despite the remaining storage difference
for literal writes. It is not full Admin Console/bootstrap acceptance.

The involved Registry, bootstrap abstract class, bootstrap interfaces and
ActionStack files were coverage checked in `kaltura-rigel-18.20.0-full`, generation
2026-09-25T12:19:00Z, with metadata-match/no-recorded-gap; relevant source was read.

## Evidence and reproduction

- `storage.json`: original native/Registry storage probes in both runtimes/modes.
- `cast-parity.json`: retained full Registry failure on PHP8.3, pass on 7.4.
- `bootstrap.json`: passing bounded bootstrap-container comparisons.
- `rejected-properties.json`: failure of the __set candidate on both versions.
- `claude-initial.txt`, `claude-followup.txt`: CLI advisory responses.

```bash
# Lab only, with cast-only candidate prepared:
python3 tools/php83/patch-tests/collect.py /tmp/registry-bootstrap.json \
  --case registry-bootstrap
python3 tools/php83/patch-tests/collect.py /tmp/registry.json --case registry
# The second command is expected to fail its strict PHP8.3 parity comparison.
```

All 38 offline tests pass. Both lab Registry files were restored to original
hash `304ba8242c81790f11dadcf7a39e63b7047f8ea33fc3de03b748cab70397b48d`
after collection. Main, `.20` and the JSON-only exp2 ZIP remain untouched.
Next: assess application-visible literal-property/alias/subclass use and runtime
diagnostics before selecting a bounded repair or requesting acceptance of a
specific native-engine behavior change. No broad migration task is complete.

# Targeted compatibility reference

Read for an actual PHP compatibility finding. Check the official page for the
specific version and exact construct; this is a navigation checklist, not an
exhaustive analyzer or replacement for source/runtime evidence.

- [PHP8.0 migration](https://www.php.net/manual/en/migration80.php): removed syntax/
  functions, callability, type/value and error behavior compared with7.4.
- [PHP8.1 migration](https://www.php.net/manual/en/migration81.php): internal
  interface return types, null passed to internal functions and signature issues.
- [PHP8.2 migration](https://www.php.net/manual/en/migration82.php): dynamic
  properties and legacy object behavior; avoid blanket attributes as suppression.
- [PHP8.3 migration](https://www.php.net/manual/en/migration83.php): target-specific
  behavior, including date/time exceptions; test exercised edge cases.
- [PHPCompatibility](https://github.com/PHPCompatibility/PHPCompatibility): use the
  project-pinned tool with testVersion=7.4-8.3 and classify findings by exact file.
- [Rector](https://getrector.com/documentation): optional AST repair aid, not an
  automatic dependency/framework upgrade or proof of preserved semantics.

A deprecation does not universally become a fatal error in the next minor
release. Language additions are not automatically breaking changes. Do not carry
forward generic claims about tool coverage percentages or blanket performance
improvements. Reproduce actual diagnostics with E_ALL, retain triage, and compare
explicit values/types rather than normalizing away differences.

Legacy hotspots to inspect only when implicated: generated ORM signatures and
save hooks, serialized/customData objects, autoload composition, optional/required
arguments, numeric/string/null/false API contracts and configured cache backends.

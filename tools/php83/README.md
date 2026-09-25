# Phase-1 PHP audit tools

These tools collect evidence, not application fixes. Use only an isolated lab.
No package postinst hooks or Kaltura application entrypoints are executed by the
syntax collector. It records every PHP-like file hash, return code and diagnostic.

```sh
# Guest has Python 3 and PHP 8.3; root is an already verified/extracted archive
# or a root assembled with dpkg-deb -x (NOT dpkg -i).
python3 lint-tree.py /path/to/tree /path/to/lint.json --php php8.3 --workers 4
```

`short_open_tag=1` and `error_reporting=E_ALL` are explicit. Symlinks are excluded.
The collector exits successfully when collection finishes even if files fail
lint: inspect `failed_count`. A passing file does not prove runtime compatibility.

## Pinned static analyzer

Run as an unprivileged user in the isolated lab, never in the Kaltura application:

```sh
cd analyzer
composer install --no-interaction --no-plugins --no-scripts
vendor/bin/phpcs --config-set installed_paths ../../phpcompatibility/php-compatibility,../../phpcsstandards/phpcsutils
vendor/bin/phpcs -i
vendor/bin/phpcs /path/to/tree --standard=PHPCompatibility \
  --runtime-set testVersion 7.4-8.3 --extensions=php,phtml,inc,php5 \
  --parallel=4 --report=json --report-file=/path/to/findings.json
```

`composer.lock` pins all dependency references; scripts/plugins are disabled and
standards are registered explicitly. Initial toolchain: PHPCompatibility
10.0.0-alpha2 (`e0f0e5a3dc819a4a0f8d679a0f2453d941976e18`) and PHPCS 4.0.4.
Composer is a lab-only tool; no Composer update is run in application packaging.

The analyzer is prerelease software with incomplete coverage. Findings are
candidates requiring manual triage, including legacy code that may already be
incompatible with 7.4. `testVersion=7.4-8.3` reports incompatibility anywhere in
that range, not only regressions introduced after the baseline. PHPCS status 3
can mean findings, not analyzer failure; always verify the JSON/totals.

References: [tagged dependency constraints](https://github.com/PHPCompatibility/PHPCompatibility/blob/10.0.0-alpha2/composer.json),
[release including PHP 8.3 checks](https://github.com/PHPCompatibility/PHPCompatibility/releases/tag/10.0.0-alpha2),
[coverage limitations](https://github.com/PHPCompatibility/PHPCompatibility#php-version-support).

## Test destination boundary

`lab_target.py` permits only literal `.74` or `.83` URLs matching the selected
lab identity, rejects userinfo/other ports/control characters, disables ambient
proxies and refuses all automatic redirects. This is a guard for the new
synthetic workload client, not a retrofit of the legacy sanity script.

```sh
python3 -m unittest discover -s tools/php83 -p 'test_*.py'
```

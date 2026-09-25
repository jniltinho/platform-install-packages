# PHP 7.4 compiler and native tokenizer control — held 43-file batch

Primary corrected run `compiler74-primary-r2.json` passed **86 compiler checks**
(43 original, 43 candidate) and **43 native PHP 7.4 tokenizer proofs**. All compiler
and token-verifier exits are zero, with no incomplete cases. The native tokenizer
confirms 153 offset pairs / 306 punctuation-byte changes; all other paired bytes
and tokens remain identical. `verify-tokens.php` was copied unchanged from the
existing verifier and its staged hash is retained.

This executes PHP `-l` and the reviewed tokenizer verifier, **not application
source bodies**. The token proof is within one PHP version; its token counts are
not assumed identical to PHP 8.3's tokenizer implementation. Actual class behavior
is a separate, three-file corpus; this check does not expand runtime coverage.

All original files emitted compiler diagnostics; one candidate still does:
`vendor/symfony/vendor/pake/pakeYaml.class.php`, line 54, contains the deprecated
old-style `pakeYAMLNode` constructor. Its compiler exit remains zero. This warning
is retained and not an acceptance waiver. E_ALL and short tags are explicit;
`-n` prevents ambient configuration and only JSON/tokenizer modules are added
for the verifier itself. The compiler invocations remain minimal `-n -l`.

The final stage `/home/vagrant/php-curly-compiler74-r2` is read-only inside the
unprivileged network-denied systemd runner. All 132 staged file identities,
interpreter, explicit JSON/tokenizer modules and linked libraries are verified
before and after. The exact outer SSH/systemd command, including stage-identity
hash guard, is in `compiler74-command-r2.json`; use a new report filename for any
independent repeat. The final identity JSON hash is
`88391be85bb3a18b81cc991947035ce42ea138e7d0b4b451e699d1c9f0ce32a0`.

The unsuccessful first attempt is preserved: module import assumed a deeper
repository path than `/audit/curly74`, causing IndexError before any test ran.
`compiler74-primary.exit` is 1; its traceback, initial script and original stage
remain. The correction only resolves repository paths for preparation, not remote
scan mode. A fresh r2 stage was used; no initial evidence was overwritten. Six
local inventory/path controls pass, and a separate shallow-mount module-import
regression control passes. No application or token-verifier source was changed.

No SQL, configured application, baseline service state, production machine,
package, CI, release or merge was changed. Both task and application acceptance
remain open. Independent CLI repeats/reviews must be evaluated separately.

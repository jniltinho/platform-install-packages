# Fixed-key credential parser revision 2

Actual previous runtime rejected the native DB credential shape before state creation, prepare or apply. This is a parser compatibility correction, not a DB application failure or privacy pass. Exact previous parser/runtime bytes are preserved beside this report.

The pinned original `configurations/db.template.ini` (SHA256 `ddc6b3c5b290a35a63f6ac60240c57b89394189dd5521a16318344ec8b5c9036`) substitutes `@DB1_PASS@` unquoted. The prior base64-like character allowlist was not justified by that template. The revised bounded subset accepts printable nonspace ASCII punctuation with 15–256 bytes, retaining quote/escape/comment/placeholder rejection and conservatively rejecting apostrophes, dollar signs and INI-expression operators, fixed key/DSN/host checks, duplicate rejection and no value/hash output. This is not a general INI parser. Unsupported shapes still fail closed. No actual password was read locally.

The original root-password regex already accepted actual LF correctly. The raw-regex spelling and exact newline removal clarify its contract; regressions distinguish actual LF from literal backslash-n and reject CRLF/multiple newlines. No original newline defect is claimed.

Runtime changes only the parser literal pin. Author local tests: 12 credential, 17 profile, 4 log adapter, all exit 0. Independent reviewer was notified of frozen pins. Actual Claude attempt is separate and must not be called successful until terminal evidence. No VM action or retry by this agent.

Final consolidated restrictions also reject braces/equals/brackets, non-tab/LF/CRLF control bytes before line parsing, and unquoted DSN strings. Quoted password and CRLF fixtures pass. Actual Claude terminal exit 0 executed 10 tests on intermediate parser27a3, returned CHANGES_REQUIRED for ambiguous INI syntax; it did not approve final source. Final correction is independently reviewed separately. No raw CLI transcript is included.

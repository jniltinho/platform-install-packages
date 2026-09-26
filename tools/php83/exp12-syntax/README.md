# Exp12 paired compile-only nonregression (NOT_EXECUTED)

Versioned from the completed exp11 harness; old tools/evidence stay unchanged.
Verified exp11/exp12 ZIP pins and exact three changed source identities are frozen.
Each scan selects all11784 PHP-like files, invokes native PHP8.3 -n -l only,
with E_ALL, short tags, read-only binds, private network and no application body.
Three changed targets already compiled in exp11: this is runtime-repair compiler
nonregression, NOT a claim of three newly accepted files. Require both variants'
seven existing rejections unchanged, every unchanged-source outcome/diagnostic
identical and all three changed targets accepted without diagnostic changes.
Native execution and independent repeat remain pending ownership and review.
No SOAP extension is needed: -n parser-only PHP, never an include or bootstrap.

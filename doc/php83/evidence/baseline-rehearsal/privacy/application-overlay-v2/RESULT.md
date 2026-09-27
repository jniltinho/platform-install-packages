# Actual installation attempt and recovery — overlay NOT installed

V1 stopped before backups/service stops/writes because a third PHP daemon was
observed. V2 added the exact package-pinned Sphinx population controller and PID
file. Independent review executed 17 local tests; no VM operation by reviewer.

V2 temporarily installed all four policy sources, then rejected its immediate
post-start inventory despite all five start commands returning zero. Automated
rollback stopped services but its 30-second quiescence wait expired. These are
real failures: guest exit 2, FAILED_RECOVERY_REQUIRED_NO_AUTH; launcher exit 0
is not acceptance. No causal attribution of daemon timing is proven.

Immediately subsequent safe inspection found no affected processes. Authorized
manual rollback verified staged after hashes, every original backup hash and
original metadata, restored four sources in reverse order, and restarted the
five reviewed components. All starts returned zero. A bounded readiness poll
observed Apache plus all three application scripts after 0.51 seconds. This is
process readiness, not application/business-function acceptance.

`manual-recovery.json` and `recovery-post-audit.json` show original source hashes
and metadata restored, Apache/Monit active, reviewed disk logger/config-cache
audit passing again. System configuration bytes were stable during recovery;
no retroactive pre-install configuration-byte proof is invented. All service
outputs stay in the guest's root-private backup directory. Two batch-start
commands emitted stderr; content has not been triaged and is not silently waived.

No authentication, nonce, USER or upload was executed. The installed application
currently uses the restored published originals, not the privacy overlay. No
logs were removed, no diagnostics disabled, no package/release assets changed.
Manual recovery was an inline bounded SSH Python operation recorded in the tool
ledger, not a claimed pre-frozen executable. No new application attempt is
authorized by this result itself.

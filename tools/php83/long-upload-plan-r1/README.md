# Long fixture upload plan — local preparation only

`plan.py` is a pure, sequential plan for the already generated synthetic fixture:
117,210,794 bytes, SHA256
`611e3644fb56fc1f12ddccd1d889258d249e36a4eca445451c16d13f5c5f5b07`.
It produces 112 contiguous parts of at most 1 MiB. It does not open the fixture,
verify its bytes, contact an API, create a token, upload, or retry a request.
Caller-supplied identity arguments are not physical file verification.

## Native source basis

Pinned Rigel-18.20.0 archive SHA256:
`58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28`.
Direct reads were used because graph coverage for these application files was
missing; the graph indexes the packaging checkout, not this extracted tree.

- `api_v3/services/UploadTokenService.php`:
  `129537b34f525e443ceb834890908fa9bbc28a50e32f74e2a24474cd5bb2aef1`,
  lines 70–97: initial `resume=false`, subsequent `resume=true`, explicit offset,
  and a final chunk carrying the remaining bytes are supported by the interface.
- `alpha/apps/kaltura/lib/kUploadTokenMgr.php`:
  `a1800965f9622bfdf49ffab3419563301863f9b0c3507c7712bc42fa5fa7cc71`,
  lines 118–215 and 406–435: move versus resume paths, partial/full state handling,
  and explicit resume offsets. Automatic finalization can change behavior and
  must be verified in a future token policy; this planner does not disable it.
- `api_v3/lib/types/enums/KalturaUploadTokenStatus.php`:
  `b3f15f19333d3644bbc3ff36d5bd10317690eccd90e465b5adf8c840f76f60f3`:
  PENDING=0, PARTIAL_UPLOAD=1, FULL_UPLOAD=2, CLOSED=3, TIMED_OUT=4, DELETED=5.

## Execution requirements not supplied here

A future executor must independently verify actual file bytes and stable identity,
lab target and source pins, TLS, privacy coverage, ownership and token settings,
finite request/overall budgets, acknowledged byte counts/status, and cleanup.
`require_next` only validates the caller's sequential counter. It cannot prove a
remote acknowledgement, prevent a caller lying about state, or provide persistent
idempotence. Any ambiguous mutation response stops execution; do not replay it
merely because the native API documents resume functionality.

No media acceptance, worker completion, task closure, production or release
permission follows from these local tests.

Run: `python3 -B -m unittest discover -s tools/php83/long-upload-plan-r1 -v`.

# Retained fixture failure

Initial `../../codex.json` reports exp8 and exp9 exit 255 and functional false.
The corresponding `probe.php` here passed a positional array to the named
`:p1` placeholder in the input-array INSERT. Native MySQL PDO rejects that with
SQLSTATE HY093. The corrected fixture supplies `array('p1' => 23)`; no application
patch, expected row values, error suppression or acceptance criterion changed.
`../../codex-r2.json` records the successful fresh-owned-DB rerun.

The original fixture hash is recorded in the initial report's harness map.
Initial log hashes and diagnostic locations are retained; raw application logs
were not persisted. A separate transient diagnostic rerun confirmed the named
binding mismatch and stopped its owned SQL unit before the corrected rerun.

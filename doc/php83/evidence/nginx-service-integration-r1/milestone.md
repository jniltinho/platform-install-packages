# Actual D3 nginx installation — bounded lab milestone

2026-09-28. Normal offline APT installed exactly `kaltura-nginx
1.23.0-1+php83lab3` in the verified `.83` laboratory. Both independently checked
builds have SHA256 `c52b28cd2aa081a8254089cb5d32ab72b177975a95f5b23b021600cce375bc19`.
Upstream data archive is unchanged; the derivative postinst applies the pinned
lab-only rendered configuration and supervised service overlay.

Actual coordinator execution exited 0. One root nginx master and five workers
were observed; listeners were exactly `.83:88` and `.83:1935`. HTTP status probe
returned 200, synthetic missing HLS path returned 404. Four log files were scanned,
one safe access record and two closed error events observed, zero findings.
Nginx was then stopped; Apache, Monit, MariaDB and Elasticsearch remained active.
All seven terminal checks passed; worker hold and private metadata were preserved.
See `actual-execution.json` for sanitized results and terminal/cohort hashes.

## Review and tests

- Exact renderer: 10 local tests independently passed (includes prior six tests).
- Service wrapper: 11 tests independently passed.
- Post-render helper: seven independent tests passed (temporary ownership calls
  mocked; not an earlier claim of guest execution).
- Package builder: five tests and actual independent archive comparison passed;
  two outputs identical and only control Version/postinst changed.
- D3 executor: seven tests independently passed, final exact delta reviewed at
  `a013992d1329df3f072d321cc2aeebe985c4bf3cf000ca5c8c2864d7aa36b99f`.
- Separate actual cached-container privilege fixture observed a real worker
  datagram, root master, UID/GID7373 worker and denied private sink access.
- Separate actual `.83` synthetic systemd test confirmed main SIGKILL terminates
  its sleep child. This is cgroup evidence, not nginx-specific SIGKILL acceptance.
- Actual Claude renderer review stopped at its turn limit (exit1, incomplete).
  Actual Claude privilege-fixture review found an initial evidence gap; the author
  corrected it with a real worker-PID-linked datagram test. That follow-up was
  actual execution, not a second completed CLI review.

## Remaining scope

The nginx service is intentionally bounded to 120 seconds and was stopped after
this probe. RTMP publishing was not exercised or released; retained callbacks
must not be triggered before their separate worker gate. TLS, media ingestion,
full playback/authentication, operational rotation and continuous-service behavior
remain unaccepted. The kaltura-server metapackage is next. No production changes,
release approval, complete three-distro acceptance or full recovery rehearsal is
implied. OpenSpec remains 4/51; no new completion email was sent.

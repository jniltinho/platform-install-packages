# Cache repair and contained Elasticsearch installation attempt

The coordinator executed the independently reviewed cache-write R2 repair.
Exit 0; exact one-placeholder replacement, privacy scan and worker hold passed;
Apache and Monit were restarted successfully. Fifteen local tests were independently
rerun. R1 remains recorded as rejected by preflight metadata review, not executed.
The original source postinst typo still requires a future fresh-artifact correction.

After a new coherent checkpoint, D2 guard passed and normal offline APT attempted
kaltura-elasticsearch 7.17-1+php83lab4. The process exited 78. Prestart configuration
hardening succeeded, but Elasticsearch failed with AccessDeniedException under
/opt/kaltura/log/elasticsearch: the existing private parent root:www-data01770
correctly excludes daemon uid112. Package status is iF, not configured successfully.
The executor stopped Apache, Monit and Elasticsearch; MariaDB remains active;
workers remain held. All five final privacy/metadata/canary observations passed.

Both the pre-attempt cache-fixed snapshot and a separate contained-failure snapshot
were saved. No restore, partial APT retry, worker release, public package release,
production change or task closure occurred. The operator has been asked to approve
restoring only the lab to the pre-attempt checkpoint before a reviewed new candidate.
A separate private daemon-log-path derivative is being prepared locally; it is not
included here and not accepted by this milestone.

This commit includes scoped repair source/tests/public-template and sanitized
receipts. The previously prepared broader installer/helper chain is not packaged
as a reproducible release by this evidence commit. Private logs, VM snapshot
payloads, generated secret configuration and SQL data are intentionally excluded.
Full OpenSpec status remains 4/51 complete, 47 open.

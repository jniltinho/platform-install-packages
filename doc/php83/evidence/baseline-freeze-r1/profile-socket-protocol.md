# Profile 14 stored relationship, separate from API authorization

The corrected native API type did not resolve the profile response in actual
V2 observation. No raw response or API exception was exported. The cause is
unknown; missing partnerId is not supported (that would fail, not take the
unresolved branch). SQL metadata must not be relabeled API authorization success.

After independent review root may execute frozen `profile_socket.py` through the
existing strict SSH transport as `sudo -n python3 -B -`, source on stdin and a
bounded outer timeout. No new deployment/immutable stage is necessary. It performs
no API authentication, upload, profile writes or service actions.

Before reading the existing private DB password, the observer verifies .74
hostname/address and protected-host exclusion, exact two profile TableMap source
hashes, observed socket 111:110:0777 and datadir 111:110:0755. It uses first-argument
`--defaults-file` pointing to a root600 anonymous memfd, explicit Unix socket and
no password argv/environment. The private source file is read via directory-fd
NOFOLLOW with root700 parents and root600 single-link regular file checks.

An identity-only SELECT validates DB hostname, root@localhost, database kaltura,
configured /var/lib/mysql/ and exact /run or /var/run mysqld socket alias before
any application SELECT. A second connection repeats identity within a read-only
transaction, fixed three application SELECTs and max_statement_time=3. Output is
bounded to 32KiB, process deadline20s, no stderr content exported. Total5 SELECTs.
Source queries read only the exact existing entry102/profile14 and configured
flavor IDs (128 rows plus overflow sentinel). Unknown ownership/cardinality or
raw strings fail closed. Empty configured flavors remains explicit empty.

The public output contains fixed entry identity, numeric profile/partner/status/
type/flavor IDs, deleted-state boolean and api_authorization_verified=false.
It does not read names/custom_data or substitute configured flavors for actual
produced assets. Native runtime/permission/performance acceptance remains open.

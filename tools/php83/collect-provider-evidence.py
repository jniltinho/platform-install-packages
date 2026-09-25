#!/usr/bin/env python3
"""Offline validation of bounded CLI/web provider smoke evidence, not T4 acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import re

RUNS = {"noble": ("ubuntu", "apache2handler"),
        "resolute": ("ubuntu", "apache2handler"), "remi": ("rocky", "fpm-fcgi")}

# Independent coverage oracle: do not infer required coverage from the log itself.
REQUIRED_MODULES = frozenset({
    "bcmath", "ctype", "curl", "dom", "fileinfo", "filter", "gd", "gmp",
    "iconv", "intl", "json", "ldap", "libxml", "mbstring", "mysqli", "mysqlnd",
    "openssl", "pcre", "pdo", "pdo_mysql", "posix", "session", "simplexml",
    "sockets", "ssh2", "tokenizer", "xml", "xmlreader", "xmlwriter", "xsl", "zip",
    "zlib", "apcu", "memcache", "zend opcache",
})
SMOKE_KEYS = frozenset({"pdo_mysql", "json", "mbstring", "gmp", "bcmath", "xml",
                        "gd", "curl", "intl", "zip", "ldap", "ssh2", "memcache",
                        "apcu", "opcache"})


class EvidenceError(ValueError):
    """Malformed or failed evidence; messages deliberately exclude raw log content."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def unique_position(lines, marker):
    positions = [i for i, line in enumerate(lines) if line == marker]
    require(len(positions) == 1, f"Expected exactly one {marker}")
    return positions[0]


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key")
        result[key] = value
    return result


def parse_run(log, exit_text, distro, web_sapi):
    require(exit_text.strip() == "0", "Probe exit status is not zero")
    lines = log.splitlines()
    reports = {}
    last = -1
    nonce = None
    for method in ("CLI", "GET", "POST"):
        begin = unique_position(lines, f"PHP83_PROVIDER_{method}_BEGIN")
        end = unique_position(lines, f"PHP83_PROVIDER_{method}_END")
        require(last < begin < end, f"Invalid {method} marker order")
        last = end
        try:
            result = json.loads("\n".join(lines[begin + 1:end]),
                                object_pairs_hook=reject_duplicate_keys)
        except (json.JSONDecodeError, UnicodeError):
            raise EvidenceError(f"Invalid {method} JSON") from None
        require(isinstance(result, dict), f"Invalid {method} object")
        require(type(result.get("schema")) is int and result["schema"] == 1,
                f"Invalid {method} schema")
        require(result.get("ok") is True, f"Failed {method} result")
        sapi = "cli" if method == "CLI" else web_sapi
        require(result.get("sapi") == sapi and result.get("expected_sapi") == sapi,
                f"Invalid {method} SAPI")
        require(result.get("method") == method, f"Invalid {method} method")
        version = result.get("php")
        require(isinstance(version, str) and re.fullmatch(r"8\.3\.\d+(?:[-+~.][\w.+~:-]+)?", version),
                f"Invalid {method} PHP version")
        current_nonce = result.get("nonce")
        require(isinstance(current_nonce, str) and bool(current_nonce.strip()),
                f"Missing {method} nonce")
        require(nonce is None or current_nonce == nonce, f"Mismatched {method} nonce")
        nonce = current_nonce
        modules, required = result.get("modules"), result.get("required")
        for name, values in (("modules", modules), ("required", required)):
            require(isinstance(values, list) and bool(values)
                    and all(isinstance(v, str) and bool(v.strip()) for v in values),
                    f"Invalid {method} {name}")
        expected_modules = REQUIRED_MODULES | ({"pcntl"} if method == "CLI" else set())
        require({m.casefold() for m in required} == expected_modules,
                f"Incomplete or unexpected {method} required extension declarations")
        require({m.casefold() for m in required} <= {m.casefold() for m in modules},
                f"Missing {method} required extension")
        require(result.get("failures") == [], f"Nonempty {method} failures")
        smoke = result.get("smoke")
        require(isinstance(smoke, dict) and set(smoke) == SMOKE_KEYS
                and all(value is True for value in smoke.values()),
                f"Failed or absent {method} smoke")
        # Retain only bounded structured probe fields, never arbitrary surrounding logs.
        reports[method] = {key: result[key] for key in
                           ("schema", "ok", "php", "sapi", "expected_sapi", "method",
                            "nonce", "modules", "required", "smoke", "failures")}
        reports[method]["ini"] = result.get("ini")
        reports[method]["scanned_ini"] = result.get("scanned_ini")
    negative = unique_position(lines, "PHP83_PROVIDER_NEGATIVE_POST_OK")
    complete = unique_position(lines, f"PHP83_PROVIDER_COMPLETE {distro}")
    require(last < negative < complete, "Invalid negative/completion marker order")
    require(sum(line.startswith("PHP83_PROVIDER_COMPLETE ") for line in lines) == 1,
            "Unexpected extra provider completion marker")
    return {"ok": True, "distro": distro, "probes": reports,
            "negative_post_rejected": True}


def collect(input_dir):
    runs = {}
    for name, (distro, sapi) in RUNS.items():
        log_path, exit_path = input_dir / f"{name}.log", input_dir / f"{name}.exit"
        try:
            raw_log, raw_exit = log_path.read_bytes(), exit_path.read_bytes()
            report = parse_run(raw_log.decode("utf-8"), raw_exit.decode("ascii"), distro, sapi)
        except (OSError, UnicodeError):
            raise EvidenceError(f"{name}: missing or unreadable evidence file") from None
        except EvidenceError as error:
            raise EvidenceError(f"{name}: {error}") from None
        report["files"] = {path.name: {"sha256": hashlib.sha256(data).hexdigest(),
                                      "bytes": len(data)}
                           for path, data in ((log_path, raw_log), (exit_path, raw_exit))}
        runs[name] = report
    return {"schema": 1, "ok": True, "scope": "provider-cli-web-synthetic-smoke-only",
            "full_T4_01_acceptance": False,
            "limitations": ["Not application, Kaltura package installation, reboot or release acceptance",
                            "Does not independently verify binary ABI or package origin"],
            "runs": runs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = collect(args.input_dir)
    except EvidenceError as error:
        report = {"schema": 1, "ok": False, "error": str(error),
                  "scope": "provider-cli-web-synthetic-smoke-only", "full_T4_01_acceptance": False}
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

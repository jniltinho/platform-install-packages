"""Synthetic fail-closed tests; no containers, network or installation."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("provider_evidence", Path(__file__).with_name("collect-provider-evidence.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture(sapi="apache2handler", distro="ubuntu", mutate=None):
    lines = []
    for method in ("CLI", "GET", "POST"):
        current_sapi = "cli" if method == "CLI" else sapi
        required = sorted(MODULE.REQUIRED_MODULES | ({"pcntl"} if method == "CLI" else set()))
        data = dict(schema=1, ok=True, php="8.3.30-1", sapi=current_sapi,
                    expected_sapi=current_sapi, method=method, nonce="synthetic-nonce",
                    modules=[m.upper() for m in required], required=required,
                    failures=[], smoke={key: True for key in MODULE.SMOKE_KEYS}, ini="/test/php.ini",
                    scanned_ini="/test/test.ini")
        if mutate:
            mutate(method, data)
        lines += [f"PHP83_PROVIDER_{method}_BEGIN", json.dumps(data), f"PHP83_PROVIDER_{method}_END"]
    return "\n".join(lines + ["PHP83_PROVIDER_NEGATIVE_POST_OK", f"PHP83_PROVIDER_COMPLETE {distro}"])


class ProviderEvidenceTests(unittest.TestCase):
    def parse(self, log, status="0\n"):
        return MODULE.parse_run(log, status, "ubuntu", "apache2handler")

    def bad_field(self, field, value):
        with self.assertRaises(MODULE.EvidenceError):
            self.parse(fixture(mutate=lambda method, data: data.update({field: value}) if method == "POST" else None))

    def test_positive_and_case_insensitive_modules(self):
        self.assertTrue(self.parse(fixture())["ok"])

    def test_three_files_and_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, (distro, sapi) in MODULE.RUNS.items():
                (root / f"{name}.log").write_text(fixture(sapi, distro))
                (root / f"{name}.exit").write_text("0\n")
            report = MODULE.collect(root)
            self.assertEqual(len(report["runs"]), 3)
            self.assertEqual(len(report["runs"]["remi"]["files"]["remi.log"]["sha256"]), 64)
            self.assertFalse(report["full_T4_01_acceptance"])

    def test_missing_marker(self):
        with self.assertRaises(MODULE.EvidenceError): self.parse(fixture().replace("PHP83_PROVIDER_GET_END", ""))

    def test_duplicate_marker(self):
        with self.assertRaises(MODULE.EvidenceError): self.parse(fixture() + "\nPHP83_PROVIDER_CLI_BEGIN")

    def test_wrong_php(self): self.bad_field("php", "8.4.1")
    def test_wrong_sapi(self): self.bad_field("sapi", "cli")
    def test_wrong_expected_sapi(self): self.bad_field("expected_sapi", "cli")
    def test_missing_module(self): self.bad_field("modules", ["PDO"])
    def test_wrong_nonce(self): self.bad_field("nonce", "different")
    def test_empty_nonce(self): self.bad_field("nonce", "")
    def test_false_smoke(self): self.bad_field("smoke", {"pdo_mysql": False})
    def test_null_smoke(self): self.bad_field("smoke", {"pdo_mysql": None})
    def test_numeric_smoke(self): self.bad_field("smoke", {"pdo_mysql": 1})
    def test_empty_smoke(self): self.bad_field("smoke", {})
    def test_failed_result(self): self.bad_field("ok", False)
    def test_failures(self): self.bad_field("failures", ["failed"])
    def test_wrong_method(self): self.bad_field("method", "GET")
    def test_boolean_schema(self): self.bad_field("schema", True)

    def test_reduced_required_list(self): self.bad_field("required", ["pdo_mysql"])

    def test_missing_smoke_key(self):
        self.bad_field("smoke", {key: True for key in MODULE.SMOKE_KEYS if key != "ldap"})

    def test_missing_cli_pcntl_declaration(self):
        with self.assertRaises(MODULE.EvidenceError):
            self.parse(fixture(mutate=lambda method, data:
                data.update(required=sorted(MODULE.REQUIRED_MODULES)) if method == "CLI" else None))

    def test_extra_smoke_key(self):
        self.bad_field("smoke", dict.fromkeys(MODULE.SMOKE_KEYS | {"invented"}, True))

    def test_exit_nonzero(self):
        with self.assertRaises(MODULE.EvidenceError): self.parse(fixture(), "1\n")

    def test_bad_negative(self):
        with self.assertRaises(MODULE.EvidenceError): self.parse(fixture().replace("NEGATIVE_POST_OK", "NEGATIVE_POST_FAILED"))

    def test_wrong_distro(self):
        with self.assertRaises(MODULE.EvidenceError): self.parse(fixture(distro="rocky"))

    def test_multiple_json(self):
        with self.assertRaises(MODULE.EvidenceError): self.parse(fixture().replace("PHP83_PROVIDER_CLI_END", "{}\nPHP83_PROVIDER_CLI_END"))

    def test_multiline_json(self):
        log = fixture().replace(', "ok":', ',\n "ok":')
        self.assertTrue(self.parse(log)["ok"])

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(MODULE.EvidenceError): MODULE.collect(Path(directory))

    def test_duplicate_json_key(self):
        with self.assertRaises(MODULE.EvidenceError): self.parse(fixture().replace('"schema": 1', '"schema": 1, "schema": 1'))


if __name__ == "__main__":
    unittest.main()

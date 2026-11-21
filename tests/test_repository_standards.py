import importlib.util
import tempfile
import unittest
from pathlib import Path


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[1]
audit = load_module("audit_script", ROOT / "scripts" / "audit.py")
badges = load_module("badges_script", ROOT / "scripts" / "badges.py")


class RepositoryStandardsTests(unittest.TestCase):
    def test_current_repository_passes_required_document_audit(self):
        report = audit.audit(ROOT)
        self.assertEqual(report["missing"], [])

    def test_verified_technology_detection_matches_repository_configuration(self):
        detected = {name: version for name, unused_color, unused_logo, version in badges.tech(ROOT)}
        self.assertEqual(detected["Python"], "3.15")
        self.assertEqual(detected["Django"], "6.1.3")
        self.assertIn("SQLite", detected)
        self.assertIn("Docker", detected)
        self.assertIn("Docker Compose", detected)
        self.assertEqual(detected["Terraform"], "1.17.2")
        self.assertIn("AWS target", detected)

    def test_badge_apply_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# Demo\n\nBody\n", encoding="utf-8")
            (root / "requirements.txt").write_text("Django~=6.1.3\n", encoding="utf-8")
            (root / "Dockerfile").write_text("FROM python:3.15-slim\n", encoding="utf-8")
            (root / "compose.yaml").write_text("services:\n  web:\n    environment:\n      DJANGO_DB_PATH: /tmp/db.sqlite3\n", encoding="utf-8")
            changed, outcome = badges.apply(root, write=True)
            self.assertTrue(changed)
            self.assertEqual(outcome, "updated")
            changed, outcome = badges.apply(root, write=True)
            self.assertFalse(changed)
            self.assertEqual(outcome, "unchanged")

    def test_malformed_badge_markers_fail_safely(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "# Demo\n\n<!-- madmallard-badges:start -->\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                badges.apply(root, write=False)


    def test_repository_has_no_legacy_video_platform_branding(self):
        forbidden = ("you" + "tube", "yt" + "clone", "drakeg/" + "yt" + "clone")
        ignored_dirs = {".git", ".venv", "node_modules", "__pycache__"}
        matches = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or any(part in ignored_dirs for part in path.parts):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            lowered = text.lower()
            for term in forbidden:
                if term in lowered:
                    matches.append(f"{path.relative_to(ROOT)}: {term}")
        self.assertFalse(matches, "Legacy branding remains:\n" + "\n".join(matches))
        self.assertFalse((ROOT / "yt").exists(), "Legacy top-level yt package must not exist")


if __name__ == "__main__":
    unittest.main()

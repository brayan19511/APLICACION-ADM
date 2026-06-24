import unittest
from pathlib import Path

from core.update_service import GitHubReleaseUpdater


class UpdaterTests(unittest.TestCase):
    def test_github_digest_is_used(self):
        updater = GitHubReleaseUpdater()
        digest = "a" * 64
        asset = {"name": "ADM.exe", "digest": f"sha256:{digest}"}
        self.assertEqual(updater._asset_digest(asset, [asset]), digest)

    def test_installer_resets_pyinstaller_environment(self):
        source = Path("core/update_service.py").read_text(encoding="utf-8")
        self.assertIn('clean_environment["PYINSTALLER_RESET_ENVIRONMENT"] = "1"', source)
        self.assertIn('if name.startswith("_PYI")', source)


if __name__ == "__main__":
    unittest.main()

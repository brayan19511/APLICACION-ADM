import unittest

from core.update_service import GitHubReleaseUpdater


class UpdaterTests(unittest.TestCase):
    def test_github_digest_is_used(self):
        updater = GitHubReleaseUpdater()
        digest = "a" * 64
        asset = {"name": "ADM.exe", "digest": f"sha256:{digest}"}
        self.assertEqual(updater._asset_digest(asset, [asset]), digest)


if __name__ == "__main__":
    unittest.main()

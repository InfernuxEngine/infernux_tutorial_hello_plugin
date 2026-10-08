"""Run the real release shell step against a local GitHub CLI boundary."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseImmutabilityTests(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        if os.name == "nt":
            git = shutil.which("git")
            self.assertIsNotNone(git, "Git for Windows is required to run the release shell step")
            self.bash = Path(git).resolve().parents[1] / "bin/bash.exe"
        else:
            self.bash = shutil.which("bash")
        self.assertTrue(self.bash and Path(self.bash).is_file(), "Bash is required for release workflow tests")
        workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        publish = workflow.split("      - name: Publish GitHub Release assets\n", 1)[1]
        script = publish.split("        run: |\n", 1)[1]
        (self.root / "release.sh").write_text(
            "set -e\n" + "\n".join(line[10:] for line in script.splitlines()) + "\n",
            encoding="utf-8",
        )
        (self.root / "bin").mkdir()
        (self.root / "dist").mkdir()
        (self.root / "published").mkdir()
        (self.root / "dist/studio.demo.inxpkg").write_bytes(b"candidate archive")
        (self.root / "dist/infernux-plugin-release.json").write_bytes(b"candidate manifest")
        # The adapter implements both the current and legacy CLI routes. An
        # overwrite attempt would change the baseline and make the test fail.
        adapter = '''#!/usr/bin/env bash
set -eu
printf '%s\\n' "$*" >> calls.txt
case "$1:$2" in
  release:view)
    test -f published/archive.inxpkg
    ;;
  release:create)
    if test -f published/archive.inxpkg; then
      echo "release already exists" >&2
      exit 23
    fi
    cp "$4" published/archive.inxpkg
    cp "$5" published/manifest.json
    ;;
  release:upload)
    cp "$4" published/archive.inxpkg
    cp "$5" published/manifest.json
    ;;
  *) exit 24 ;;
esac
'''
        path = self.root / "bin/gh"
        path.write_text(adapter, encoding="utf-8")
        path.chmod(0o755)

    def publish(self):
        environment = dict(os.environ, GITHUB_REF_NAME="v0.1.0", PACKAGE_NAME="studio.demo.inxpkg")
        return subprocess.run(
            [str(self.bash), "--noprofile", "--norc", "-c",
             'export PATH="$PWD/bin:$PATH"; exec bash release.sh'],
            cwd=self.root, env=environment, capture_output=True, text=True,
        )

    def test_duplicate_release_fails_without_overwriting_either_asset(self):
        archive = self.root / "published/archive.inxpkg"
        manifest = self.root / "published/manifest.json"
        archive.write_bytes(b"original archive")
        manifest.write_bytes(b"original manifest")
        result = self.publish()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(archive.read_bytes(), b"original archive")
        self.assertEqual(manifest.read_bytes(), b"original manifest")

    def test_new_release_publishes_the_archive_and_matching_manifest(self):
        result = self.publish()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / "published/archive.inxpkg").read_bytes(), b"candidate archive")
        self.assertEqual((self.root / "published/manifest.json").read_bytes(), b"candidate manifest")
        self.assertEqual(
            (self.root / "calls.txt").read_text(encoding="utf-8").splitlines(),
            ["release create v0.1.0 dist/studio.demo.inxpkg dist/infernux-plugin-release.json --verify-tag --generate-notes"],
        )


if __name__ == "__main__":
    unittest.main()

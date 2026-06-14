import tempfile
import unittest
from pathlib import Path

from scripts import repo_snapshot


class RepoSnapshotTest(unittest.TestCase):
    def create_file(self, root: Path, relative_path: str, content: str) -> None:
        file_path = root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    def test_java_entrypoint_detection_does_not_mislabel_service(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_file(root, "pom.xml", "<project />")
            self.create_file(
                root,
                "src/main/java/com/demo/DemoApplication.java",
                "public class DemoApplication { public static void main(String[] args) {} }",
            )
            self.create_file(
                root,
                "src/main/java/com/demo/service/OrderService.java",
                "class OrderService {}",
            )

            snapshot = repo_snapshot.build_snapshot(root)

            self.assertEqual(
                snapshot["likely_entrypoints"],
                ["src/main/java/com/demo/DemoApplication.java"],
            )
            self.assertEqual(
                snapshot["area_hints"]["entrypoints"],
                ["src/main/java/com/demo/DemoApplication.java"],
            )
            self.assertEqual(
                snapshot["area_hints"]["services"],
                ["src/main/java/com/demo/service/OrderService.java"],
            )

    def test_ignored_directories_are_excluded_from_counts_and_languages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_file(root, "src/main.py", 'if __name__ == "__main__": print(1)')
            self.create_file(root, "node_modules/pkg/a.js", "console.log(1)")
            self.create_file(root, "target/generated/App.java", "class App {}")

            snapshot = repo_snapshot.build_snapshot(root)

            self.assertEqual(snapshot["counts"]["files"], 1)
            self.assertEqual(snapshot["top_level"]["dirs"], ["src"])
            self.assertEqual(snapshot["likely_entrypoints"], ["src/main.py"])
            self.assertEqual(
                snapshot["languages"],
                [{"language": "Python", "files": 1, "examples": ["src/main.py"]}],
            )

    def test_tooling_repo_exposes_docs_script_and_agent_hints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.create_file(root, "README.md", "# demo")
            self.create_file(root, "references/core-guidelines.md", "# core")
            self.create_file(root, "scripts/repo_snapshot.py", "print('ok')")
            self.create_file(root, "agents/openai.yaml", "name: demo")

            snapshot = repo_snapshot.build_snapshot(root)
            area_hints = snapshot["area_hints"]

            self.assertIn("docs_assets", area_hints)
            self.assertIn("automation_assets", area_hints)
            self.assertIn("agent_assets", area_hints)
            self.assertEqual(area_hints["docs_assets"], ["references/core-guidelines.md"])
            self.assertEqual(area_hints["automation_assets"], ["scripts/repo_snapshot.py"])
            self.assertEqual(area_hints["agent_assets"], ["agents/openai.yaml"])


if __name__ == "__main__":
    unittest.main()

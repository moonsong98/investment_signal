from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DockerComposeConfigTests(unittest.TestCase):
    def test_event_log_directory_is_mounted_to_host(self) -> None:
        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("./data/events:/app/data/events", compose)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from investment.research import generate_research_notes, is_level_3_event


def event_payload(severity: str) -> dict:
    return {
        "event_id": f"{severity}-event-id",
        "received_at": "2026-05-06T00:00:00+00:00",
        "event_at": "2026-05-05T20:30:00+00:00",
        "source": "tradingview",
        "symbol": "BTC",
        "asset_type": "crypto",
        "timeframe": "1D",
        "alert_type": "earnings_shock_support_breakdown",
        "severity": severity,
        "notification": {"sent": False, "dry_run": True, "reason": "dry_run"},
        "payload": {
            "message": "Level 3 sample event",
            "price": 100000,
            "secret": "[REDACTED]",
        },
    }


class ResearchNoteGeneratorTests(unittest.TestCase):
    def test_is_level_3_event(self) -> None:
        self.assertTrue(is_level_3_event({"severity": "level_3"}))
        self.assertFalse(is_level_3_event({"severity": "level_2"}))

    def test_generate_research_notes_only_for_level_3(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = root / "events"
            output_dir = root / "research"
            event_dir.mkdir()
            event_dir.joinpath("2026-05-06.jsonl").write_text(
                json.dumps(event_payload("level_2")) + "\n"
                + json.dumps(event_payload("level_3")) + "\n",
                encoding="utf-8",
            )

            notes = generate_research_notes(event_dir, output_dir)

            self.assertEqual(len(notes), 1)
            note_text = notes[0].path.read_text(encoding="utf-8")
            self.assertIn("Generated Research Note Draft", note_text)
            self.assertIn("Human Review: required", note_text)
            self.assertIn("LLM Used: false", note_text)
            self.assertIn("Do not place live orders", note_text)
            self.assertNotIn("level_2-event-id", note_text)

    def test_generated_note_does_not_publish_secret_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            event_dir = root / "events"
            output_dir = root / "research"
            event_dir.mkdir()
            payload = event_payload("level_3")
            payload["payload"]["token"] = "[REDACTED]"
            event_dir.joinpath("2026-05-06.jsonl").write_text(
                json.dumps(payload) + "\n",
                encoding="utf-8",
            )

            notes = generate_research_notes(event_dir, output_dir)
            note_text = notes[0].path.read_text(encoding="utf-8")

            self.assertNotIn("secret", note_text.lower())
            self.assertNotIn("token", note_text.lower())
            self.assertNotIn("[REDACTED]", note_text)


if __name__ == "__main__":
    unittest.main()

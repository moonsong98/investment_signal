"""Research note generation."""

from investment.research.note_generator import (
    GeneratedNote,
    generate_research_notes,
    is_level_3_event,
    iter_event_logs,
    render_note,
)

__all__ = [
    "GeneratedNote",
    "generate_research_notes",
    "is_level_3_event",
    "iter_event_logs",
    "render_note",
]

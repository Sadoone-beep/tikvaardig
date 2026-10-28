"""The measuring core, without a window: keys in, numbers out. Time comes from outside."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Stats:
    elapsed: float
    typed: int        # all entered characters (excluding backspaces)
    correct: int      # characters currently correct
    wrong: int        # characters currently wrong
    errors: int       # errors ever made (even if corrected)
    finished: bool

    @property
    def wpm(self) -> float:
        """Net: only correct characters count, 5 characters = 1 word."""
        if self.elapsed <= 0:
            return 0.0
        return self.correct / 5 / (self.elapsed / 60)

    @property
    def raw_wpm(self) -> float:
        if self.elapsed <= 0:
            return 0.0
        return self.typed / 5 / (self.elapsed / 60)

    @property
    def accuracy(self) -> float:
        """Percentage of all keystrokes that were right the first time."""
        if self.typed == 0:
            return 100.0
        return max(0.0, 100.0 * (self.typed - self.errors) / self.typed)


@dataclass
class Session:
    text: str
    duration: float | None = None   # seconds; None = until the text is finished
    pos: int = 0
    typed: int = 0
    errors: int = 0
    state: list[bool] = field(default_factory=list)  # per typed position: correct?
    started_at: float | None = None
    ended_at: float | None = None

    def start(self, now: float) -> None:
        if self.started_at is None:
            self.started_at = now

    @property
    def running(self) -> bool:
        return self.started_at is not None and self.ended_at is None

    def time_left(self, now: float) -> float | None:
        if self.duration is None:
            return None
        if self.started_at is None:
            return self.duration
        return max(0.0, self.duration - (now - self.started_at))

    def key(self, ch: str, now: float) -> bool:
        """Process one character. Returns whether it was correct. Starts the clock on the first key."""
        if self.ended_at is not None or self.pos >= len(self.text):
            return False
        self.start(now)
        ok = ch == self.text[self.pos]
        self.state.append(ok)
        self.pos += 1
        self.typed += 1
        if not ok:
            self.errors += 1
        if self.pos >= len(self.text):
            self.ended_at = now
        elif self.duration is not None and now - self.started_at >= self.duration:
            self.ended_at = now
        return ok

    def backspace(self) -> None:
        if self.ended_at is not None or self.pos == 0:
            return
        self.pos -= 1
        self.state.pop()

    def tick(self, now: float) -> bool:
        """Time up? Then finish. Returns whether the session is done."""
        if self.running and self.duration is not None and now - self.started_at >= self.duration:
            self.ended_at = now
        return self.ended_at is not None

    def stats(self, now: float) -> Stats:
        if self.started_at is None:
            elapsed = 0.0
        else:
            end = self.ended_at if self.ended_at is not None else now
            elapsed = end - self.started_at
            if self.duration is not None:
                elapsed = min(elapsed, self.duration)
        correct = sum(1 for ok in self.state if ok)
        return Stats(elapsed=elapsed, typed=self.typed, correct=correct,
                     wrong=len(self.state) - correct, errors=self.errors, finished=self.ended_at is not None)

    def expected(self) -> str:
        return self.text[self.pos] if self.pos < len(self.text) else ""

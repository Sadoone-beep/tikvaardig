import json
import os
import random
import sys
import tempfile
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_TMP = tempfile.TemporaryDirectory()
os.environ["TIKVAARDIG_DATA_DIR"] = _TMP.name
os.environ["TIKVAARDIG_HEADLESS"] = "1"

from tikvaardig import history, texts  # noqa: E402
from tikvaardig.engine import Session  # noqa: E402


class EngineTests(unittest.TestCase):
    def type_all(self, s: Session, text: str, t0: float, per_char: float) -> float:
        now = t0
        for ch in text:
            s.key(ch, now)
            now += per_char
        return now

    def test_wpm_and_accuracy(self):
        s = Session("abcde fghij klmno pqrst uvwxy", duration=None)  # 29 characters
        self.type_all(s, s.text, t0=100.0, per_char=1.0)  # 28 s for 29 characters
        st = s.stats(200.0)
        self.assertTrue(st.finished)
        self.assertEqual(st.correct, 29)
        self.assertEqual(st.errors, 0)
        self.assertAlmostEqual(st.elapsed, 28.0)
        self.assertAlmostEqual(st.wpm, 29 / 5 / (28 / 60), places=3)
        self.assertEqual(st.accuracy, 100.0)

    def test_errors_and_backspace(self):
        s = Session("hallo", duration=None)
        s.key("h", 0.0)
        s.key("x", 0.5)          # wrong
        self.assertEqual(s.errors, 1)
        s.backspace()
        s.key("a", 1.0)          # corrected
        s.key("l", 1.5)
        s.key("l", 2.0)
        s.key("o", 2.5)
        st = s.stats(3.0)
        self.assertTrue(st.finished)
        self.assertEqual(st.correct, 5)
        self.assertEqual(st.wrong, 0)
        self.assertEqual(st.errors, 1)       # the error still counts for accuracy
        self.assertEqual(st.typed, 6)
        self.assertAlmostEqual(st.accuracy, 100 * 5 / 6)

    def test_timed_session_stops(self):
        s = Session("a" * 1000, duration=10.0)
        self.assertEqual(s.time_left(0.0), 10.0)
        now = self.type_all(s, "a" * 50, t0=0.0, per_char=0.1)   # 5 s
        self.assertTrue(s.running)
        self.assertAlmostEqual(s.time_left(now), 5.0)
        self.assertFalse(s.tick(7.0))
        self.assertTrue(s.tick(10.0))
        self.assertFalse(s.key("a", 11.0))     # after the end a key does nothing
        st = s.stats(50.0)
        self.assertAlmostEqual(st.elapsed, 10.0)
        self.assertEqual(st.correct, 50)
        self.assertAlmostEqual(st.wpm, 60.0)   # 50 characters = 10 words in 10 s

    def test_no_time_before_start(self):
        s = Session("abc", duration=30)
        st = s.stats(123.0)
        self.assertEqual((st.elapsed, st.wpm, st.accuracy), (0.0, 0.0, 100.0))
        self.assertEqual(s.expected(), "a")
        s.backspace()  # nothing to erase
        self.assertEqual(s.pos, 0)


class TextTests(unittest.TestCase):
    def test_make_text(self):
        rng = random.Random(1)
        t = texts.make_text("nl", 400, rng)
        self.assertGreaterEqual(len(t), 400)
        self.assertNotIn("  ", t)
        sentences = t.split(". ")
        self.assertGreater(len(sentences), 3)
        e = texts.make_text("en", 2000, rng)   # more than the pool: repeats without immediate duplicates
        words = e.split(". ")
        for a, b in zip(words, words[1:]):
            self.assertNotEqual(a, b)
        self.assertIn(texts.single("en", rng), texts.EN)

    def test_pools_are_plain(self):
        for pool in (texts.NL, texts.EN):
            self.assertGreaterEqual(len(pool), 25)
            for s in pool:
                self.assertTrue(s[0].isupper() and s[-1] in ".?!", s)
                self.assertTrue(all(ord(ch) < 128 for ch in s), s)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        for p in (history.path(), os.path.join(history.data_dir(), history.OLD_FILE)):
            if os.path.exists(p):
                os.remove(p)

    def test_add_best_summary(self):
        self.assertEqual(history.load(), [])
        self.assertEqual(history.summary()["count"], 0)
        self.assertIsNone(history.best())
        history.add("60 seconds", "nl", 42.26, 96.5, 60, 211, datetime(2026, 10, 28, 1, 0))
        history.add("60 seconds", "nl", 55.0, 91.0, 60, 275, datetime(2026, 10, 28, 1, 5))
        history.add("30 seconds", "en", 70.0, 99.0, 30, 175, datetime(2026, 10, 28, 1, 10))
        items = history.load()
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["wpm"], 42.3)
        self.assertEqual(history.best()["wpm"], 70.0)
        self.assertEqual(history.best(mode="60 seconds")["wpm"], 55.0)
        sm = history.summary()
        self.assertEqual(sm["count"], 3)
        self.assertEqual(sm["best_wpm"], 70.0)
        self.assertAlmostEqual(sm["avg_wpm"], 55.8, places=1)

    def test_migrates_old_dutch_file(self):
        old = os.path.join(history.data_dir(), history.OLD_FILE)
        with open(old, "w", encoding="utf-8") as f:
            json.dump([{"when": "2026-10-28 01:00", "mode": "60 seconden", "lang": "nl",
                        "wpm": 40.0, "accuracy": 95.0, "seconds": 60, "chars": 200}], f)
        items = history.load()
        self.assertEqual(items[0]["mode"], "60 seconds")
        self.assertFalse(os.path.exists(old))
        self.assertTrue(os.path.exists(history.path()))
        self.assertEqual(history.best(mode="60 seconds")["wpm"], 40.0)


class GuiTests(unittest.TestCase):
    def test_full_session_in_window(self):
        from tikvaardig.gui import TikvaardigApp
        clock = [1000.0]
        app = TikvaardigApp(clock=lambda: clock[0])
        app.mode.set("Full text")
        app.new_session()
        text = app.session.text
        self.assertGreater(len(text), 200)

        class Ev:
            def __init__(self, ch, keysym="x"):
                self.char = ch
                self.keysym = keysym

        for ch in text[:10]:
            app.on_key(Ev(ch))
            clock[0] += 0.2
        app.on_key(Ev("", "BackSpace"))
        self.assertEqual(app.session.pos, 9)
        for ch in text[9:]:
            app.on_key(Ev(ch))
            clock[0] += 0.2
        self.assertTrue(app.session.stats(clock[0]).finished)
        self.assertTrue(app.saved)
        self.assertIn("Done", app.message.cget("text"))
        self.assertEqual(len(history.load()), 1)
        app.refresh_history()
        self.assertEqual(len(app.table.get_children()), 1)
        app.destroy()


if __name__ == "__main__":
    unittest.main()

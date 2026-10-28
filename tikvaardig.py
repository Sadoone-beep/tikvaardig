"""Tikvaardig - typing trainer.

  python tikvaardig.py          window
  python tikvaardig.py stats    history in the terminal
  python tikvaardig.py test     test suite
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def main(argv: list[str]) -> int:
    if not argv:
        from tikvaardig.gui import main as gui_main
        return gui_main()
    if argv[0] == "test":
        import unittest
        suite = unittest.defaultTestLoader.discover(os.path.join(ROOT, "tests"), top_level_dir=ROOT)
        return 0 if unittest.TextTestRunner(verbosity=1).run(suite).wasSuccessful() else 1
    if argv[0] == "stats":
        from tikvaardig import history
        items = history.load()
        sm = history.summary(items)
        print(f"{sm['count']} sessions, average {sm['avg_wpm']} wpm, best {sm['best_wpm']} wpm")
        for it in items[-10:]:
            print(f"{it['when']}  {it['mode']:12} {it['lang']}  {it['wpm']:5.1f} wpm  {it['accuracy']:5.1f}%")
        return 0
    print(__doc__)
    return 0 if argv[0] in ("-h", "--help", "help") else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

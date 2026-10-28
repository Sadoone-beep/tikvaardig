# Tikvaardig

A typing trainer that just measures. Pick 30 seconds, 60 seconds or a full text, start
typing, and watch your words per minute, accuracy and errors live. Correctly typed
characters turn green, mistakes red, and Backspace works the way you expect.

Every session goes into your history: a table, a bar chart of the last thirty sessions
(your best in yellow) and your average. Texts in English and Dutch, made of ordinary
sentences instead of tongue-twisters.

```
start.bat
python tikvaardig.py stats
python tikvaardig.py test
```

Needs Python 3.12+ with tkinter (included in the standard Windows installer). No other
dependencies.

**How it counts:** words per minute = correct characters ÷ 5 ÷ minutes (net, like most
typing tests). Accuracy = share of keystrokes that were right the first time; a corrected
mistake still counts against you. History lives in `%LOCALAPPDATA%\Tikvaardig\history.json`.

The measuring core (`tikvaardig/engine.py`) has no window and gets the time from outside,
so the tests run with a fake clock.

## Name

"Tikvaardig" is Dutch for "skilled at typing".

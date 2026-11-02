> Walkthrough written with Claude (Sonnet 5.5); completed and verified by running the code.

# Command

## Concept

**Problem:** with direct method calls (`editor.insert("x")`) the action vanishes after it runs: no undo, no history, no replay, no queueing. **Solution:** turn each action into an **object** with `execute()` and `undo()`; an invoker runs commands and keeps the history. **Trade-off:** one class per action, every command needs a correct undo, and undoing external effects (a sent email, a charged card) may be impossible.

## Full Line-by-Line Breakdown

**Receiver.** `TextDocument` does the real work (`insert`, `delete`, `substring`) and knows nothing about commands.

**Commands.** `InsertCommand` undoes by deleting the inserted range. `DeleteCommand` **remembers the removed text in `execute()`**, before changing anything, because `undo()` needs it.

**Invoker `Editor`.** Two stacks give undo **and** redo. Running a new command clears the redo stack (a new action ends the old "future").

```
after two inserts:   "Hello world"
after delete:        "world"
undo (delete):       "Hello world"
undo (insert world): "Hello"
redo (insert world): "Hello world"
new action:          "Hello world!"
redo now possible?   false   (a new action cleared the redo history)
```

**Macro command.** `MacroCommand` groups steps into one undoable unit and undoes them in **reverse** order:

```
macro executed:      ">> Hello world! <<"
one undo reverts both: "Hello world!"
```

**A bug I made while writing this (kept as a lesson).** The first version created the second insert with `doc.length()`, giving `">> Hello wor <<ld!"`. A command stores its position when it is **created**, but it runs after the first insert already added 3 characters, so the position must be `doc.length() + 3`. Commands that capture state early can become stale; this is a real design risk of the pattern.

**Job queue.** `Runnable` is a simple command (no undo): three queued jobs ran in order.

## Key Rules

1. Every command stores what it needs to undo itself.
2. Save the "before" state at `execute()` time.
3. Undo a macro in reverse order.
4. A new action clears the redo history.

## Gotchas Recap

- Stale captured positions or state (the bug above).
- `undo()` for irreversible effects is a lie: use a compensating action and name it honestly.
- Command history can grow without limit: cap it in real editors.

## Why This Structure Exists

Insert, delete, undo/redo, macro, queue: each step adds one capability the pattern exists for. Exit test: with no need for undo, queueing or logging, a direct call or a lambda is simpler than a command class.

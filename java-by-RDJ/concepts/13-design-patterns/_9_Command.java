// Completed and verified (compiled and run on JDK 21). Written with Claude (Sonnet 5.5); authorship disclosed.
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/**
 * COMMAND: turn a request ("do this") into an OBJECT, so it can be stored, queued, logged, and UNDONE.
 * PROBLEM  : you call methods directly (editor.insert("x")), so the action vanishes after it runs: no undo,
 *            no history, no replay, no delayed or batched execution.
 * SOLUTION : each action becomes an object with execute() (and undo()). An "invoker" runs commands and keeps
 *            the history. The receiver (the thing being changed) only knows how to do the real work.
 * TRADE-OFF: one class per action (lots of small classes), and every command needs a correct undo; undo of
 *            external effects (sent emails, charged cards) may be impossible.
 */
public class _9_Command {

    // ============================================
    // THE RECEIVER - does the real work, knows nothing about commands
    // ============================================

    static class TextDocument {
        private final StringBuilder text = new StringBuilder();

        void insert(int position, String s) {
            text.insert(position, s);
        }

        void delete(int from, int to) {
            text.delete(from, to);
        }

        String substring(int from, int to) {
            return text.substring(from, to);
        }

        int length() {
            return text.length();
        }

        @Override
        public String toString() {
            return "\"" + text + "\"";
        }
    }

    // ============================================
    // THE COMMAND INTERFACE
    // ============================================

    interface Command {
        void execute();

        void undo();
    }

    static class InsertCommand implements Command {
        private final TextDocument doc;
        private final int position;
        private final String text;

        InsertCommand(TextDocument doc, int position, String text) {
            this.doc = doc;
            this.position = position;
            this.text = text;
        }

        public void execute() {
            doc.insert(position, text);
        }

        public void undo() {
            doc.delete(position, position + text.length());
        }
    }

    static class DeleteCommand implements Command {
        private final TextDocument doc;
        private final int from;
        private final int to;
        private String removed;                                    // remembered so we can put it back

        DeleteCommand(TextDocument doc, int from, int to) {
            this.doc = doc;
            this.from = from;
            this.to = to;
        }

        public void execute() {
            removed = doc.substring(from, to);                     // save BEFORE changing: undo needs it
            doc.delete(from, to);
        }

        public void undo() {
            doc.insert(from, removed);
        }
    }

    // ============================================
    // THE INVOKER - runs commands and keeps history (two stacks give undo AND redo)
    // ============================================

    static class Editor {
        private final Deque<Command> undoStack = new ArrayDeque<>();
        private final Deque<Command> redoStack = new ArrayDeque<>();

        void run(Command c) {
            c.execute();
            undoStack.push(c);
            redoStack.clear();                                     // a new action ends the old "future"
        }

        boolean undo() {
            if (undoStack.isEmpty()) return false;
            Command c = undoStack.pop();
            c.undo();
            redoStack.push(c);
            return true;
        }

        boolean redo() {
            if (redoStack.isEmpty()) return false;
            Command c = redoStack.pop();
            c.execute();
            undoStack.push(c);
            return true;
        }
    }

    // ============================================
    // A SECOND USE: commands as a QUEUE of work (and a MACRO that groups commands)
    // ============================================

    static class MacroCommand implements Command {
        private final List<Command> steps;

        MacroCommand(List<Command> steps) {
            this.steps = List.copyOf(steps);
        }

        public void execute() {
            for (Command c : steps) c.execute();
        }

        public void undo() {
            for (int i = steps.size() - 1; i >= 0; i--) steps.get(i).undo();   // undo in REVERSE order
        }
    }

    public static void main(String[] args) {

        TextDocument doc = new TextDocument();
        Editor editor = new Editor();

        editor.run(new InsertCommand(doc, 0, "Hello"));
        editor.run(new InsertCommand(doc, 5, " world"));
        System.out.println("after two inserts:   " + doc);

        editor.run(new DeleteCommand(doc, 0, 6));                  // removes "Hello "
        System.out.println("after delete:        " + doc);

        editor.undo();
        System.out.println("undo (delete):       " + doc);
        editor.undo();
        System.out.println("undo (insert world): " + doc);
        editor.redo();
        System.out.println("redo (insert world): " + doc);

        editor.run(new InsertCommand(doc, doc.length(), "!"));
        System.out.println("new action:          " + doc);
        System.out.println("redo now possible?   " + editor.redo() + "   (a new action cleared the redo history)");

        System.out.println("--- macro: several steps as ONE undoable unit ---");
        // GOTCHA: a command stores its position when it is CREATED. The second insert runs after the first
        // one has already added 3 characters, so its position must account for that (+ 3).
        // (My first version used doc.length() alone and inserted " <<" in the MIDDLE of the text.)
        Command shout = new MacroCommand(List.of(
                new InsertCommand(doc, 0, ">> "),
                new InsertCommand(doc, doc.length() + 3, " <<")));
        editor.run(shout);
        System.out.println("macro executed:      " + doc);
        editor.undo();
        System.out.println("one undo reverts both: " + doc);

        System.out.println("--- commands as a job queue ---");
        Deque<Runnable> jobs = new ArrayDeque<>();                 // Runnable IS a simple command (no undo)
        List<String> done = new ArrayList<>();
        jobs.add(() -> done.add("send invoice"));
        jobs.add(() -> done.add("update stock"));
        jobs.add(() -> done.add("notify warehouse"));
        while (!jobs.isEmpty()) {
            jobs.poll().run();
        }
        System.out.println("queued jobs ran in order: " + done);

        // ============================================
        // JDK/ecosystem examples: Runnable and Callable (a command without undo), ExecutorService.submit(task),
        // database transactions (rollback = undo), "git revert".
        //
        // WHEN IT MAKES THE CODE WORSE (exit-test material)
        // - You need no undo, no queue, no log: a direct method call (or a lambda) is simpler than a class.
        // - Actions with irreversible side effects (sending an email): an undo() that cannot truly undo is a lie.
        //   Prefer a "compensating action" (send a correction) and be honest in the name.
        // - Dozens of one-line command classes for a tiny app: lambdas as Runnable are enough.
        // ============================================
    }
}

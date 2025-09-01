#silly python
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox

CALL_WORDS = [
    ("A", "Alpha"),
    ("B", "Bravo"),
    ("C", "Charlie"),
    ("D", "Delta"),
    ("E", "Echo"),
    ("F", "Foxtrot"),
    ("G", "Golf"),
    ("H", "Hotel"),
    ("I", "India"),
    ("J", "Juliett"),
    ("K", "Kilo"),
    ("L", "Lima"),
    ("M", "Mike"),
    ("N", "November"),
    ("O", "Oscar"),
    ("P", "Papa"),
    ("Q", "Quebec"),
    ("R", "Romeo"),
    ("S", "Sierra"),
    ("T", "Tango"),
    ("U", "Uniform"),
    ("V", "Victor"),
    ("W", "Whiskey"),
    ("X", "Xray"),
    ("Y", "Yankee"),
    ("Z", "Zulu"),
]

# i didn't like writting x-ray so i guess more stuff...'
ACCEPTED_VARIANTS = {
    "Xray": ["Xray", "X-ray", "X ray"]
}


def normalize(word: str) -> str:
    return "".join(ch for ch in word.lower() if ch.isalnum())


def is_correct_guess(expected_word: str, guess: str) -> bool:
    g = normalize(guess)
    # direct match to expected
    if g == normalize(expected_word):
        return True
    # variant match
    for base, alts in ACCEPTED_VARIANTS.items():
        if expected_word == base:
            for alt in alts:
                if g == normalize(alt):
                    return True
    return False


class GameState:

    def __init__(self, mode: str):
        self.mode = mode  # 'regular' or 'endless'
        self.index = 0
        self.sequence = []
        self.current_letter = None
        self.current_word = None
        self.letter_start_time = None
        self.game_start_time = None
        self.correct_count = 0
        self.total_correct_time = 0.0  # sum of per-letter elapsed durations (correct guesses only)

        if mode == "regular":
            # makes the letter order shuffle at start of regular mode
            self.sequence = list(range(len(CALL_WORDS)))
            random.shuffle(self.sequence)
        elif mode == "endless":
            self.sequence = []
        else:
            raise ValueError("i didn't code that mode in????'")


    def start(self):
        """starts the game clock and select the first letter"""
        self.game_start_time = time.perf_counter()
        self._pick_next_letter()

    def _pick_next_letter(self):
        if self.mode == "regular":
            if self.index >= len(CALL_WORDS):
                self.current_letter = None
                self.current_word = None
                self.letter_start_time = None
                return  # finished
            i = self.sequence[self.index]
        else:
            i = random.randint(0, len(CALL_WORDS) - 1)

        self.current_letter, self.current_word = CALL_WORDS[i]
        self.letter_start_time = time.perf_counter()


    def submit_guess(self, text: str):
        if text.strip().lower() == "quit":
            return False, False

        if self.current_word is None:
            return False, False

        if is_correct_guess(self.current_word, text):
            now = time.perf_counter()
            if self.letter_start_time is not None:
                self.total_correct_time += (now - self.letter_start_time)
            self.correct_count += 1

            if self.mode == "regular":
                self.index += 1
                self._pick_next_letter()
                finished = self.index >= len(CALL_WORDS)
                return True, finished
            else:
                self._pick_next_letter()
                return True, False
        else:
            return False, False


    def regular_stats(self):
        total_time = time.perf_counter() - self.game_start_time if self.game_start_time else 0.0
        avg = total_time / len(CALL_WORDS) if CALL_WORDS else 0.0
        return total_time, avg


    def endless_average(self):
        if self.correct_count == 0:
            return 0.0
        return self.total_correct_time / self.correct_count


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("this is a title | hmmm yes, indeed...")
        self.geometry("720x420")
        self.minsize(600, 360)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.game = None

        self.home_frame = None
        self.game_frame = None
        self.letter_label = None
        self.log_list = None
        self.entry = None
        self.status_label = None

        self._build_home()


    def _build_home(self):
        if self.game_frame is not None:
            self.game_frame.destroy()

        self.home_frame = ttk.Frame(self)
        self.home_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        for i in range(2):
            self.home_frame.columnconfigure(i, weight=1)
        self.home_frame.rowconfigure(0, weight=1)

        title = ttk.Label(self.home_frame, text="Bravo Oscar Yankee - Kilo India Sierra Sierra Echo Romeo :3", font=("TkDefaultFont", 20, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 24))

        regular_btn = ttk.Button(self.home_frame, text="Normal", command=self._start_regular)
        endless_btn = ttk.Button(self.home_frame, text="Endless", command=self._start_endless)

        regular_btn.grid(row=1, column=0, sticky="nsew", padx=(0, 8), ipady=24)
        endless_btn.grid(row=1, column=1, sticky="nsew", padx=(8, 0), ipady=24)


    def _start_regular(self):
        self._build_game_ui(mode="regular")


    def _start_endless(self):
        self._build_game_ui(mode="endless")


    def _build_game_ui(self, mode: str):
        if self.home_frame is not None:
            self.home_frame.destroy()

        self.game = GameState(mode)
        self.game.start()

        self.game_frame = ttk.Frame(self)
        self.game_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        self.game_frame.columnconfigure(0, weight=1)
        self.game_frame.rowconfigure(1, weight=1)  # log expands

        # big letter like what chelsea told me to do
        self.letter_label = ttk.Label(self.game_frame, text=self.game.current_letter or "", font=("TkDefaultFont", 72, "bold"))
        self.letter_label.grid(row=0, column=0, sticky="n", pady=(0, 8))

        self.log_list = tk.Listbox(self.game_frame, height=8)
        self.log_list.grid(row=1, column=0, sticky="nsew")

        self.entry = ttk.Entry(self.game_frame)
        self.entry.grid(row=2, column=0, sticky="ew", pady=(8, 8))
        self.entry.focus_set()
        self.entry.bind("<Return>", self._on_submit)

        self.status_label = ttk.Label(self.game_frame, text=self._status_text())
        self.status_label.grid(row=3, column=0, sticky="ew")

        self.bind("<Escape>", lambda e: self.destroy())


    def _status_text(self) -> str:
        if not self.game:
            return ""
        if self.game.mode == "endless":
            avg = self.game.endless_average()
            return f"Endless mode | Correct: {self.game.correct_count} | Avg seconds/word: {avg:.2f}"
        else:
            remaining = len(CALL_WORDS) - self.game.index
            return f"Regular mode | Remaining: {remaining}"


    def _on_submit(self, event=None):
        if not self.game:
            return
        text = self.entry.get().strip()
        if text.lower() == "quit":
            self.destroy()
            return

        correct, finished = self.game.submit_guess(text)
        if correct:
            self._log_line(f"[OK] {text}")
        else:
            self._log_line(f"[X] {text}")

        self.letter_label.config(text=self.game.current_letter or "")

        self.entry.delete(0, tk.END)
        self.status_label.config(text=self._status_text())

        if self.game.mode == "regular" and finished:
            total_time, avg = self.game.regular_stats()
            messagebox.showinfo(
                "Run complete",
                f"Total time: {total_time:.2f} s\nAverage time per word: {avg:.2f} s"
            )
            self._build_home()


    def _log_line(self, text: str):
        self.log_list.insert(tk.END, text)
        self.log_list.yview_moveto(1.0)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

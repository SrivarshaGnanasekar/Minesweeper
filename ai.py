import tkinter as tk
from tkinter import messagebox
import random
import heapq  # Needed for A* algorithm
import time  # For the timer

class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.is_mine = False
        self.adjacent_mines = 0
        self.is_revealed = False  # Track if the cell has been revealed

class Minesweeper:
    def __init__(self, master):
        self.master = master
        self.master.title("Minesweeper")
        self.master.state('zoomed')
        self.root = tk.Frame(self.master)
        self.root.pack(expand=True, fill=tk.BOTH)

        self.grid_size = 0  # Initialize grid_size
        self.num_mines = 0   # Initialize num_mines
        self.cells = []
        self.buttons = []
        self.first_click = True
        self.game_active = False  # Flag to track if the game is active
        self.username = ""  # Store username
        self.timer_running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.timer_label = None

        self.show_intro_page()

    def show_intro_page(self):
        self.clear_screen()
        self.intro_frame = tk.Frame(self.master, bg="#F0F8FF")  # Alice Blue
        self.intro_frame.pack(expand=True, fill=tk.BOTH)

        intro_label = tk.Label(self.intro_frame, text="Welcome to Minesweeper", font=("Helvetica", 26, "bold"),
                               bg="#F0F8FF", fg="#1E90FF")  # Dodger Blue
        intro_label.grid(row=0, column=0, pady=(30, 15), columnspan=3)

        instructions = (
            "How to Play:\n"
            "1. Left-click to reveal a cell.\n"
            "2. Right-click to flag/unflag a potential mine (not implemented in this version).\n"
            "3. Avoid clicking on mines (marked as '💣').\n"
            "4. The number on a revealed cell indicates the number of adjacent mines.\n"
            "5. Reveal all non-mine cells to win."
        )

        rules_label = tk.Label(self.intro_frame, text=instructions, font=("Calibri", 16), justify=tk.LEFT,
                               bg="#F0F8FF", fg="#000000")  # Black
        rules_label.grid(row=1, column=0, padx=20, pady=(0, 25), columnspan=3, sticky="w")

        start_button = tk.Button(self.intro_frame, text="Start Game", font=("Arial", 18), bg="#90EE90", fg="#006400",  # LightGreen, DarkGreen
                                 command=self.ask_username, padx=20, pady=10)
        start_button.grid(row=2, column=0, pady=15, columnspan=3)

        exit_button = tk.Button(self.intro_frame, text="Exit", font=("Arial", 18), bg="#F08080", fg="#8B0000",  # LightCoral, DarkRed
                                command=self.master.quit, padx=20, pady=10)
        exit_button.grid(row=3, column=0, pady=15, columnspan=3)

        back_button = tk.Button(self.intro_frame, text="Back", font=("Arial", 14), command=self.show_intro_page)
        back_button.grid(row=5, column=0, pady=10, columnspan=3)

        self.animate_example()

    def animate_example(self):
        example_frame = tk.Frame(self.intro_frame, bg="#FFFACD", bd=2, relief=tk.GROOVE)  # LemonChiffon
        example_frame.grid(row=4, column=0, pady=20, columnspan=3, padx=20)

        instruction_example_label = tk.Label(example_frame, text="Quick Example:",
                                             font=("Arial", 16, "italic"), bg="#FFFACD")
        instruction_example_label.grid(row=0, column=0, pady=(10, 5), columnspan=3)

        self.animate_buttons = []
        for r in range(3):
            row_buttons = []
            for c in range(3):
                button = tk.Button(example_frame, text='', width=3, height=1, font=("Arial", 14),
                                   bg="#D3D3D3", state=tk.DISABLED, relief=tk.SUNKEN)  # LightGray
                button.grid(row=r + 1, column=c, padx=3, pady=3)
                row_buttons.append(button)
            self.animate_buttons.append(row_buttons)

        self.cells_example = [
            [0, 1, 'X'],
            [1, 2, 1],
            [0, 1, 0]
        ]
        self.show_animation(0, 0)

    def show_animation(self, r, c):
        if r < 3:
            button = self.animate_buttons[r][c]
            button.config(bg="#ADD8E6")  # Light Blue
            self.master.after(500, lambda b=button, val=self.cells_example[r][c]: self.reveal_example_cell(b, val, r, c))
            if c == 2:
                self.master.after(1500, self.show_animation, r + 1, 0)
            else:
                self.master.after(1500, self.show_animation, r, c + 1)

    def reveal_example_cell(self, button, val, r, c):
        if val == 'X':
            button.config(text='💣', bg="#FF6347")  # Tomato
        elif isinstance(val, int):
            color = ["blue", "green", "red", "purple", "maroon", "turquoise", "black", "gray"][val % 8]
            button.config(text=str(val), bg="#E0FFFF", fg=color)  # LightCyan
        else:
            button.config(bg="#F5F5DC")  # Beige

    def ask_username(self):
        self.intro_frame.destroy()
        self.clear_screen()
        self.root.configure(bg="#B0E0E6")  # Powder Blue

        tk.Label(self.root, text="Enter Username:", font=("Georgia", 20), bg="#B0E0E6").pack(pady=15)
        self.username_entry = tk.Entry(self.root, font=("Courier New", 16), justify='center')
        self.username_entry.pack(pady=10, padx=50)
        self.username_entry.focus_set()  # Focus on the entry box

        next_button = tk.Button(self.root, text="Next", font=("Arial", 16), bg="#4682B4", fg="white",  # Steel Blue
                                 command=self.choose_difficulty, padx=15, pady=8)
        next_button.pack(pady=25)

        #back_button = tk.Button(self.root, text="Back", font=("Arial", 14), command=self.show_intro_page)
        #back_button.pack(pady=10)

    def choose_difficulty(self):
        self.username = self.username_entry.get().strip()
        if not self.username:
            messagebox.showwarning("Warning", "Please enter a username!")
            return

        self.clear_screen()
        self.root.configure(bg="#DCDCDC")  # Gainsboro

        tk.Label(self.root, text=f"Welcome {self.username}! \nChoose Difficulty:",
                 font=("Georgia", 20), bg="#DCDCDC").pack(pady=25)

        easy_button = tk.Button(self.root, text="Easy (8x8, 10 Mines)", font=("Arial", 16), bg="#3CB371", fg="white",  # MediumSeaGreen
                                 command=lambda: self.start_game(8, 10), padx=20, pady=10)
        easy_button.pack(pady=8)
        medium_button = tk.Button(self.root, text="Medium (12x12, 20 Mines)", font=("Arial", 16), bg="#F4A460", fg="white",  # SandyBrown
                                   command=lambda: self.start_game(12, 20), padx=20, pady=10)
        medium_button.pack(pady=8)
        hard_button = tk.Button(self.root, text="Hard (16x16, 40 Mines)", font=("Arial", 16), bg="#DC143C", fg="white",  # Crimson
                                 command=lambda: self.start_game(16, 40), padx=20, pady=10)
        hard_button.pack(pady=8)

        back_button = tk.Button(self.root, text="Back", font=("Arial", 14), command=self.ask_username)
        back_button.pack(pady=10)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_game(self, grid_size, num_mines):
        self.clear_screen()
        self.grid_size = grid_size
        self.num_mines = num_mines
        self.width = grid_size
        self.height = grid_size
        self.cells = [[Cell(r, c) for c in range(grid_size)] for r in range(grid_size)]
        self.buttons = [[None for _ in range(grid_size)] for _ in range(grid_size)]
        self.first_click = True
        self.game_active = True  # Reset game_active

        for r in range(grid_size):
            for c in range(grid_size):
                btn = tk.Button(self.root, text="", width=3, height=1, font=("Arial", 14),
                                command=lambda row=r, col=c: self.on_cell_click(row, col))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[r][c] = btn

        self.start_time = 0
        self.elapsed_time = 0

        # Timer Label (Right side of grid)
        self.timer_label = tk.Label(self.root, text="Time: 00:00", font=("Arial", 14), bg="#DCDCDC")
        self.timer_label.grid(row=0, column=grid_size + 1, padx=10, pady=5, sticky="w")

        # Hint Button (Right side of grid, below timer)
        hint_button = tk.Button(self.root, text="Hint", font=("Arial", 14), command=self.give_hint, bg="#FFFFE0")
        hint_button.grid(row=1, column=grid_size + 1, padx=10, pady=5, sticky="w")
        self.start_timer()

    def start_timer(self):
        self.timer_running = True
        self.start_time = time.time()
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.elapsed_time = int(time.time() - self.start_time)
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            time_str = f"Time: {minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            self.master.after(1000, self.update_timer)

    def place_mines(self, first_click_row, first_click_col):
        count = 0
        while count < self.num_mines:
            r = random.randint(0, self.height - 1)
            c = random.randint(0, self.width - 1)
            if (r, c) != (first_click_row, first_click_col) and not self.cells[r][c].is_mine:
                self.cells[r][c].is_mine = True
                count += 1
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.height and 0 <= nc < self.width:
                            self.cells[nr][nc].adjacent_mines += 1

    def on_cell_click(self, r, c):
        if self.first_click:
            self.place_mines(r, c)
            self.first_click = False

        if self.cells[r][c].is_mine:
            self.reveal_board()
            self.timer_running = False
            messagebox.showinfo("Game Over",
                                f"You clicked on a mine! Game Over!\nTime taken: {self.elapsed_time} seconds")
            self.game_over(False)
        else:
            self.a_star_reveal(r, c)
            if self.check_win():
                self.reveal_board()
                self.game_over(True)
    def a_star_reveal(self, r, c):
        if not self.game_active:
            return
        open_list = []
        heapq.heappush(open_list, (0, (r, c)))
        revealed = set()

        while open_list:
            cost, (curr_r, curr_c) = heapq.heappop(open_list)
            if (curr_r, curr_c) in revealed:
                continue
            revealed.add((curr_r, curr_c))
            self.reveal_cell(curr_r, curr_c)

            if self.cells[curr_r][curr_c].adjacent_mines == 0:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < self.height and 0 <= nc < self.width and (nr, nc) not in revealed and not self.cells[nr][nc].is_revealed:
                            heapq.heappush(open_list, (cost + 1, (nr, nc)))

    def reveal_cell(self, r, c):
        if not self.game_active or self.cells[r][c].is_revealed:
            return
        btn = self.buttons[r][c]
        if btn['state'] == tk.NORMAL:
            btn['state'] = tk.DISABLED
            self.cells[r][c].is_revealed = True
            if self.cells[r][c].adjacent_mines == 0:
                btn['bg'] = "#F0F8FF"  # Alice Blue
            else:
                color = ["blue", "green", "red", "purple", "maroon", "turquoise", "black", "gray"][self.cells[r][c].adjacent_mines % 8]
                btn['text'] = str(self.cells[r][c].adjacent_mines)
                btn['bg'] = "#E0FFFF"  # LightCyan
                btn['fg'] = color

    def reveal_board(self):
        """ Reveal all cells in the board. """
        for r in range(self.height):
            for c in range(self.width):
                btn = self.buttons[r][c]
                btn['state'] = tk.DISABLED
                if self.cells[r][c].is_mine:
                    btn['text'] = '💣'
                    btn['bg'] = "#FF4500"  # OrangeRed
                elif self.cells[r][c].adjacent_mines > 0:
                    color = ["blue", "green", "red", "purple", "maroon", "turquoise", "black", "gray"][self.cells[r][c].adjacent_mines % 8]
                    btn['text'] = str(self.cells[r][c].adjacent_mines)
                    btn['bg'] ="#E0FFFF"  # LightCyan
                    btn['fg'] = color
                else:
                    btn['bg'] = "#F0F8FF"  # Alice Blue
        self.timer_running = False

    def give_hint(self):
        if not self.game_active:
            return
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if not self.cells[r][c].is_mine and not self.cells[r][c].is_revealed:
                    self.buttons[r][c].config(bg="#FFFF00")  # Yellow
                    self.master.after(200, lambda row=r, col=c: self.buttons[row][col].config(bg="SystemButtonFace"))
                    return

    def check_win(self):
        if not self.game_active:
            return True  # Game is over, no need to check further
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if not self.cells[r][c].is_mine and not self.cells[r][c].is_revealed:
                    return False
        return True

    def game_over(self, won):
        self.game_active = False  # Set game_active to False
        self.reveal_board()  # Reveal all cells

        self.clear_screen()
        if won:
            tk.Label(self.root, text=f"Congratulations, {self.username}! You Won!", font=("Arial", 24), fg="green").pack()
            tk.Label(self.root, text="🎉🎊", font=("Arial", 48)).pack()
        else:
            tk.Label(self.root, text=f"Sorry, {self.username}. You Lost!", font=("Arial", 24), fg="red").pack()
            tk.Label(self.root, text="😢", font=("Arial", 48)).pack()

        play_again_button = tk.Button(self.root, text="Play Again", font=("Arial", 18), command=self.show_difficulty_page)
        play_again_button.pack(pady=20)
        exit_button = tk.Button(self.root, text="Exit", font=("Arial", 16), bg="salmon", command=self.master.quit)
        exit_button.pack()

    def show_difficulty_page(self):
        self.clear_screen()
        self.root.configure(bg="#D3D3D3")  # Gainsboro

        tk.Label(self.root, text=f"Play Again, {self.username}! \nChoose Difficulty:",
                 font=("Georgia", 20), bg="#D3D3D3").pack(pady=25)

        easy_button = tk.Button(self.root, text="Easy (8x8, 10 Mines)", font=("Arial", 16), bg="#3CB371", fg="white",  # MediumSeaGreen
                                 command=lambda: self.start_game(8, 10), padx=20, pady=10)
        easy_button.pack(pady=8)
        medium_button = tk.Button(self.root, text="Medium (12x12, 20 Mines)", font=("Arial", 16), bg="#F4A460", fg="white",  # SandyBrown
                                   command=lambda: self.start_game(12, 20), padx=20, pady=8)
        medium_button.pack(pady=8)
        hard_button = tk.Button(self.root, text="Hard (16x16, 40 Mines)", font=("Arial", 16), bg="#DC143C", fg="white",  # Crimson
                                 command=lambda: self.start_game(16, 40), padx=20, pady=8)
        hard_button.pack(pady=8)

        back_button = tk.Button(self.root, text="Back", font=("Arial", 14), command=self.ask_username)
        back_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = Minesweeper(root)
    root.mainloop()

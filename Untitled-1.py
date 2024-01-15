import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.current_player = 'X'
        self.board = [[' ' for _ in range(4)] for _ in range(4)]

        # إضافة مكونات لعرض معلومات اللاعب الحالي والنتيجة
        self.info_label = tk.Label(root, text="Player X's turn", font=('normal', 14))
        self.info_label.grid(row=0, column=0, columnspan=3)
        
        self.result_label = tk.Label(root, text="", font=('normal', 14))
        self.result_label.grid(row=4, column=0, columnspan=3)

        self.buttons = [[None for _ in range(4)] for _ in range(4)]

        for i in range(1, 4):
            for j in range(1, 4):
                self.buttons[i][j] = tk.Button(root, text='', font=('normal', 24), width=5, height=2,
                                               command=lambda row=i, col=j: self.on_button_click(row, col))
                self.buttons[i][j].grid(row=i, column=j)

    def on_button_click(self, row, col):
        if self.board[row][col] == ' ':
            self.board[row][col] = self.current_player
            self.buttons[row][col].config(text=self.current_player)
            if self.check_winner():
                self.show_winner()
            elif self.is_board_full():
                self.show_tie()
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                self.update_info_label()

    def update_info_label(self):
        self.info_label.config(text=f"Player {self.current_player}'s turn")

    def check_winner(self):
        for i in range(1, 4):
            if all(self.board[i][j] == self.current_player for j in range(1, 4)) or \
                    all(self.board[j][i] == self.current_player for j in range(1, 4)):
                return True

        if all(self.board[i][i] == self.current_player for i in range(1, 4)) or \
                all(self.board[i][3 - i] == self.current_player for i in range(1, 4)):
            return True

        return False

    def is_board_full(self):
        return all(self.board[i][j] != ' ' for i in range(1, 4) for j in range(1, 4))

    def show_winner(self):
        self.result_label.config(text=f"Player {self.current_player} wins!")
        self.reset_board()

    def show_tie(self):
        self.result_label.config(text="It's a tie!")
        self.reset_board()

    def reset_board(self):
        for i in range(1, 4):
            for j in range(1, 4):
                self.board[i][j] = ' '
                self.buttons[i][j].config(text='')
        self.current_player = 'X'
        self.update_info_label()
        self.result_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()

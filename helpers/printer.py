class Printer():
    def __init__(self, canvas_width=0, canvas_height=0, players=None):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.players = players


    def save(self, fname, board, data):
        with open(fname) as f:
            if self.players:
                f.write(f'sente : {self.players[0]}\n')
                f.write(f'gote : {self.players[1]}\n')
            f.write(f'Nb move in game : {len(data)}\n')

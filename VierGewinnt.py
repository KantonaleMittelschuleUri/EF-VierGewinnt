import pygame
import sys
import random

# Constants
ROWS = 6
COLS = 7
CELL_SIZE = 100
WIDTH = COLS * CELL_SIZE
HEIGHT = (ROWS + 1) * CELL_SIZE  # Extra row for the Reset button
RADIUS = CELL_SIZE // 2 - 5

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

class ConnectFour:
    def __init__(self):
        self.board = [["-" for _ in range(COLS)] for _ in range(ROWS)]
        self.player = "R"  # R for Red, Y for Yellow
        self.running = True
        self.winner = None  # type: str | None
        self.winning_coords = []
        self.fullscreen = False
        self.current_scale = 1.0
        self.current_offset_x = 0
        self.current_offset_y = 0

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Connect Four")
        self.clock = pygame.time.Clock()

    def drop_piece(self, col, piece):
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == "-":
                self.board[r][col] = piece
                return r
        return -1

    def is_valid_location(self, col):
        return self.board[0][col] == "-"

    def get_valid_locations(self):
        return [c for c in range(COLS) if self.is_valid_location(c)]

    def check_winner(self, piece):
        # Horizontal
        for c in range(COLS - 3):
            for r in range(ROWS):
                if self.board[r][c] == piece and self.board[r][c+1] == piece and self.board[r][c+2] == piece and self.board[r][c+3] == piece:
                    return [(r, c), (r, c+1), (r, c+2), (r, c+3)]
        # Vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                if self.board[r][c] == piece and self.board[r+1][c] == piece and self.board[r+2][c] == piece and self.board[r+3][c] == piece:
                    return [(r, c), (r+1, c), (r+2, c), (r+3, c)]
        # Positive diagonal
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if self.board[r][c] == piece and self.board[r+1][c+1] == piece and self.board[r+2][c+2] == piece and self.board[r+3][c+3] == piece:
                    return [(r, c), (r+1, c+1), (r+2, c+2), (r+3, c+3)]
        # Negative diagonal
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if self.board[r][c] == piece and self.board[r-1][c+1] == piece and self.board[r-2][c+2] == piece and self.board[r-3][c+3] == piece:
                    return [(r, c), (r-1, c+1), (r-2, c+2), (r-3, c+3)]
        return None

    def reset_game(self):
        self.board = [["-" for _ in range(COLS)] for _ in range(ROWS)]
        self.player = "R"
        self.winner = None
        self.winning_coords = []
        print("Game Reset!")

    def draw_board(self):
        win_w, win_h = self.screen.get_size()
        
        # Calculate best scale and offset to center the board
        # Board aspect ratio is COLS / (ROWS + 1)
        board_w = COLS * CELL_SIZE
        board_h = (ROWS + 1) * CELL_SIZE
        
        scale = min(win_w / board_w, win_h / board_h)
        
        offset_x = (win_w - board_w * scale) / 2
        offset_y = (win_h - board_h * scale) / 2
        
        # Save these for click detection
        self.current_scale = scale
        self.current_offset_x = offset_x
        self.current_offset_y = offset_y

        self.screen.fill(BLACK)
        
        # Draw background
        pygame.draw.rect(self.screen, BLUE, (offset_x, offset_y + CELL_SIZE * scale, COLS * CELL_SIZE * scale, ROWS * CELL_SIZE * scale))
        
        # Draw slots
        for r in range(ROWS):
            for c in range(COLS):
                color = BLACK
                if self.board[r][c] == "R":
                    color = RED
                elif self.board[r][c] == "Y":
                    color = YELLOW
                
                center_x = offset_x + c * CELL_SIZE * scale + (CELL_SIZE // 2) * scale
                center_y = offset_y + (r + 1) * CELL_SIZE * scale + (CELL_SIZE // 2) * scale
                radius = RADIUS * scale
                
                pygame.draw.circle(self.screen, color, (int(center_x), int(center_y)), int(radius))
                
                # Highlight winning pieces
                if (r, c) in self.winning_coords:
                    pygame.draw.circle(self.screen, WHITE, (int(center_x), int(center_y)), int(radius), int(15 * scale))

        # Draw Reset Button (far right in top row)
        btn_w = (COLS * CELL_SIZE * scale) / 7
        btn_h = CELL_SIZE * scale
        
        # We only draw one button for Reset
        pygame.draw.rect(self.screen, (150, 50, 50), (offset_x + 6 * btn_w, offset_y, btn_w, btn_h))

        pygame.display.update()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.RESIZABLE)
                            print("Fullscreen Enabled")
                        else:
                            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                            print("Fullscreen Disabled")

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    
                    # Transform mouse coordinates back to virtual board coordinates
                    # Virtual board size: WIDTH x HEIGHT
                    # Transformation: mouse_x = offset_x + virtual_x * scale
                    
                    scale = self.current_scale
                    ox, oy = self.current_offset_x, self.current_offset_y
                    
                    vx = (mx - ox) / scale
                    vy = (my - oy) / scale
                    
                    # Final check: is (vx, vy) within [0, WIDTH] and [0, HEIGHT]?
                    if 0 <= vx <= WIDTH and 0 <= vy <= HEIGHT:
                        # Top row clicked (Reset Button)
                        if vy < CELL_SIZE:
                            if vx > 6 * WIDTH // 7:
                                self.reset_game()
                                continue
                        
                        # Column clicked
                        elif not self.winner:
                            col = int(vx // CELL_SIZE)
                            if 0 <= col < COLS and self.is_valid_location(col):
                                self.drop_piece(col, self.player)
                                self.winning_coords = self.check_winner(self.player) or []
                                if self.winning_coords:
                                    self.winner = self.player
                                    winner_name = "Red" if self.winner == "R" else "Yellow"
                                    print(f"Player {winner_name} Wins!")
                                elif not self.get_valid_locations():
                                    self.winner = "Draw"
                                    print("Game Draw!")
                                self.player = "Y" if self.player == "R" else "R"
            self.draw_board()
            

if __name__ == "__main__":
    game = ConnectFour()
    game.run()

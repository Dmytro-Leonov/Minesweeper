import pygame as pg
import random
import sys
sys.setrecursionlimit(2000)

# SCREEN_WIDTH, SCREEN_HEIGHT = 1900, 1000
# GRID_WIDTH, GRID_HEIGHT = 95, 50
# MINES = 1000

# SCREEN_WIDTH, SCREEN_HEIGHT = 400, 400
# GRID_WIDTH, GRID_HEIGHT = 10, 10
# MINES = 10

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
GRID_WIDTH, GRID_HEIGHT = 40, 40
MINES = 250

COLOR_RED = (255, 0, 0)
COLOR_BLACK = (0, 0, 0)


class Cell:

    def __init__(self, has_mine: bool, mines_count: int):
        self.has_mine = has_mine
        self.mines_count = mines_count
        self.revealed = False
        self.flagged = False


class Grid:
    def __init__(self, screen_width: int, screen_height: int, width: int, height: int, number_of_mines: int):
        if screen_width / width != screen_height / height:
            raise ValueError("Proportion of screen size to grid size is incorrect "
                             "screen_height / width != screen_height / height")
        elif width * height <= number_of_mines:
            raise ValueError(f"More mines than available spaces {width * height = } <= {number_of_mines = }")
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = width
        self.height = height
        self.grid = []
        self.number_of_mines = number_of_mines
        self.first_click = False
        self.cell_color = (255, 255, 255)
        self.revealed_cell_color = (160, 160, 160)
        self.mine_color = (0, 0, 0)
        self.flag_color = (255, 0, 0)
        self.colors = {
            1: (0, 0, 255),
            2: (0, 255, 0),
            3: (255, 0, 0),
            4: (20, 18, 46),
            5: (2, 7, 16),
            6: (68, 52, 58),
            7: (43, 47, 49),
            8: (0, 0, 0),
        }

        self.cell_step = int(screen_width // width)
        self.font_size = int(self.cell_step * .75)
        self.mine_radius = int(self.cell_step * .4)

        for i in range(self.height):
            for j in range(self.width):
                self.grid.append(Cell(False, 0))

    def get_cell(self, i, j):
        return self.grid[i * self.width + j]

    def display(self, surface):
        font = pg.font.Font(pg.font.get_default_font(), self.font_size)
        for i in range(0, self.height):
            for j in range(0, self.width):
                if self.get_cell(i, j).revealed:
                    pg.draw.rect(
                        surface,
                        self.revealed_cell_color,
                        (j * self.cell_step + 1, i * self.cell_step + 1, self.cell_step - 2, self.cell_step - 2)
                    )
                    mines = self.get_cell(i, j).mines_count
                    if mines > 0:
                        number = font.render(str(self.get_cell(i, j).mines_count), True, self.colors[mines])
                        surface.blit(
                            number,
                            (
                                int(j * self.cell_step + self.cell_step / 2 - number.get_width() / 2),
                                int(i * self.cell_step + self.cell_step / 2 - number.get_height() / 2.5)
                            )
                        )
                    elif self.get_cell(i, j).has_mine:
                        pg.draw.circle(
                            surface,
                            self.mine_color,
                            (
                                int(j * self.cell_step + self.cell_step / 2),
                                int(i * self.cell_step + self.cell_step / 2)
                            ),
                            self.mine_radius
                        )
                else:
                    pg.draw.rect(
                        surface,
                        self.cell_color,
                        (j * self.cell_step + 1, i * self.cell_step + 1, self.cell_step - 2, self.cell_step - 2)
                    )
                if self.get_cell(i, j).flagged:
                    pg.draw.circle(
                        surface,
                        self.flag_color,
                        (
                            int(j * self.cell_step + self.cell_step / 2),
                            int(i * self.cell_step + self.cell_step / 2)
                        ),
                        self.mine_radius
                    )

    def left_click(self, pos):
        y = pos[1] // int(self.screen_height / self.height)
        x = pos[0] // int(self.screen_width / self.width)
        if not self.first_click:
            self.first_click = True
            available_spaces = []
            for i in range(self.height):
                for j in range(self.width):
                    available_spaces.append((i, j))
            available_spaces.remove((y, x))
            for i in range(self.number_of_mines):
                mine_place = random.choice(available_spaces)
                available_spaces.remove(mine_place)
                self.get_cell(mine_place[0], mine_place[1]).has_mine = True

            for i in range(self.height):
                for j in range(self.width):
                    for k in range(i - 1, i + 2):
                        for m in range(j - 1, j + 2):
                            if 0 <= k < self.height and 0 <= m < self.width and not self.get_cell(i, j).has_mine:
                                if self.get_cell(k, m).has_mine:
                                    self.get_cell(i, j).mines_count += 1
        if not self.get_cell(y, x).flagged:
            self.open_cell(y, x)

    def right_click(self, pos):
        y = pos[1] // int(self.screen_height / self.height)
        x = pos[0] // int(self.screen_width / self.width)
        if self.get_cell(y, x).flagged:
            self.get_cell(y, x).flagged = False
        elif not self.get_cell(y, x).revealed:
            self.get_cell(y, x).flagged = True

    def open_cell(self, y, x):
        self.get_cell(y, x).revealed = True
        self.get_cell(y, x).flagged = False
        for i in range(y - 1, y + 2):
            for j in range(x - 1, x + 2):
                if 0 <= i < self.height and 0 <= j < self.width:
                    if not self.get_cell(y, x).has_mine and not self.get_cell(i, j).revealed and \
                            self.get_cell(y, x).mines_count == 0:
                        self.open_cell(i, j)

    def check_win(self):
        count = 0
        for i in range(len(self.grid)):
            if self.grid[i].revealed:
                count += 1
            if self.grid[i].revealed and self.grid[i].has_mine:
                return True, "YOU LOST"
        if count == self.width * self.height - self.number_of_mines:
            return True, "YOU WON"
        return False, ""


def main():
    pg.init()
    window = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Minesweeper")
    game_over = False
    left_mb_pressed = False
    right_mb_pressed = False
    escape = False
    end_game = False
    end_text = ""
    font_size = int(SCREEN_WIDTH / 10)
    font = pg.font.Font(pg.font.get_default_font(), font_size)
    grid = Grid(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_WIDTH, GRID_HEIGHT, MINES)
    while not game_over and not escape:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                escape = True
        if pg.mouse.get_pressed()[0] and not left_mb_pressed:
            if not end_game:
                pos = pg.mouse.get_pos()
                grid.left_click(pos)
                end_game, end_text = grid.check_win()
            else:
                end_game = False
                window.fill(COLOR_BLACK)
                grid = Grid(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_WIDTH, GRID_HEIGHT, MINES)
            left_mb_pressed = True
        if not pg.mouse.get_pressed()[0] and left_mb_pressed:
            left_mb_pressed = False
        if pg.mouse.get_pressed()[2] and not right_mb_pressed and not end_game:
            pos = pg.mouse.get_pos()
            grid.right_click(pos)
            right_mb_pressed = True
        if not pg.mouse.get_pressed()[2] and right_mb_pressed:
            right_mb_pressed = False
        grid.display(window)
        if end_game:
            text = font.render(end_text, True, COLOR_RED)
            window.blit(
                text,
                (int(SCREEN_WIDTH / 2 - text.get_width() / 2), int(SCREEN_HEIGHT / 2 - text.get_height() / 2))
            )
        if not game_over:
            pg.display.update()
    pg.quit()


if __name__ == '__main__':
    main()

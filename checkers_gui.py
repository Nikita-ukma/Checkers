# Файл: checkers_gui.py
import pygame
import sys
from checkers_interface import CheckersInterface

# Константи
WINDOW_SIZE = 800
CELL_SIZE = WINDOW_SIZE // 8
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_BROWN = (139, 69, 19)
LIGHT_BROWN = (222, 184, 135)
HIGHLIGHT_COLOR = (255, 255, 0, 128)  # Напівпрозорий жовтий

class CheckersGUI:
    """
    Графічний інтерфейс користувача для гри в шашки з використанням PyGame
    """
    def __init__(self):
        """
        Ініціалізація графічного інтерфейсу
        """
        # Ініціалізація PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Шашки")
        
        # Логіка гри
        self.interface = CheckersInterface()
        self.board = self.interface.get_initial_board()
        self.current_player = "white"
        
        # Змінні стану гри
        self.selected_piece = None
        self.possible_moves = []
        self.game_over = False
        
        # Завантаження та масштабування зображень шашок
        self.images = {
            'w': self._scale_image('assets/white_checker.png'),
            'b': self._scale_image('assets/black_checker.png'),
            'wk': self._scale_image('assets/white_king.png'),
            'bk': self._scale_image('assets/black_king.png')
        }
        
        # Таймер для оновлення екрану
        self.clock = pygame.time.Clock()
    
    def _scale_image(self, image_path):
        """
        Завантажує та масштабує зображення
        
        Args:
            image_path (str): Шлях до зображення
        
        Returns:
            pygame.Surface: Масштабоване зображення
        """
        try:
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (int(CELL_SIZE * 0.8), int(CELL_SIZE * 0.8)))
        except pygame.error:
            print(f"Не вдалося завантажити зображення: {image_path}")
            # Створюємо заглушку зображення
            surface = pygame.Surface((int(CELL_SIZE * 0.8), int(CELL_SIZE * 0.8)), pygame.SRCALPHA)
            if 'white' in image_path or 'w' in image_path:
                pygame.draw.circle(surface, WHITE, (int(CELL_SIZE * 0.4), int(CELL_SIZE * 0.4)), int(CELL_SIZE * 0.4))
                pygame.draw.circle(surface, BLACK, (int(CELL_SIZE * 0.4), int(CELL_SIZE * 0.4)), int(CELL_SIZE * 0.4), 2)
                if 'king' in image_path:
                    pygame.draw.circle(surface, RED, (int(CELL_SIZE * 0.4), int(CELL_SIZE * 0.4)), int(CELL_SIZE * 0.2))
            else:
                pygame.draw.circle(surface, BLACK, (int(CELL_SIZE * 0.4), int(CELL_SIZE * 0.4)), int(CELL_SIZE * 0.4))
                if 'king' in image_path:
                    pygame.draw.circle(surface, RED, (int(CELL_SIZE * 0.4), int(CELL_SIZE * 0.4)), int(CELL_SIZE * 0.2))
            return surface
    
    def draw_board(self):
        """
        Малює шашкову дошку
        """
        for row in range(8):
            for col in range(8):
                # Обчислюємо колір клітинки
                if (row + col) % 2 == 0:
                    color = LIGHT_BROWN
                else:
                    color = DARK_BROWN
                
                # Малюємо клітинку
                pygame.draw.rect(self.screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                
                # Додаємо координати для зручності
                if row == 7:
                    # Додаємо літери внизу дошки
                    font = pygame.font.SysFont('Arial', 12)
                    letter = chr(ord('a') + col)
                    text = font.render(letter, True, WHITE if color == DARK_BROWN else BLACK)
                    self.screen.blit(text, (col * CELL_SIZE + 5, (row + 1) * CELL_SIZE - 15))
                
                if col == 0:
                    # Додаємо цифри зліва від дошки
                    font = pygame.font.SysFont('Arial', 12)
                    number = str(8 - row)
                    text = font.render(number, True, WHITE if color == DARK_BROWN else BLACK)
                    self.screen.blit(text, (5, row * CELL_SIZE + 5))
    
    def draw_pieces(self):
        """
        Малює шашки на дошці
        """
        for row in range(8):
            for col in range(8):
                piece = self.interface.get_piece(self.board, col + 1, row + 1)
                if piece != "empty":
                    # Центруємо шашку в клітинці
                    image = self.images.get(piece)
                    if image:
                        x = col * CELL_SIZE + (CELL_SIZE - image.get_width()) // 2
                        y = row * CELL_SIZE + (CELL_SIZE - image.get_height()) // 2
                        self.screen.blit(image, (x, y))
    
    def highlight_selected(self):
        """
        Підсвічує вибрану шашку та можливі ходи
        """
        if self.selected_piece:
            # Координати вибраної шашки
            x, y = self.selected_piece
            # Перетворюємо на координати екрану
            screen_x = (x - 1) * CELL_SIZE
            screen_y = (y - 1) * CELL_SIZE
            
            # Створюємо напівпрозорий прямокутник
            highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (255, 255, 0, 128), highlight.get_rect())
            self.screen.blit(highlight, (screen_x, screen_y))
            
            # Підсвічуємо можливі ходи
            for move in self.possible_moves:
                to_x, to_y = move
                screen_x = (to_x - 1) * CELL_SIZE
                screen_y = (to_y - 1) * CELL_SIZE
                
                # Створюємо напівпрозорий прямокутник для можливого ходу
                move_highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(move_highlight, (0, 255, 0, 128), move_highlight.get_rect())
                self.screen.blit(move_highlight, (screen_x, screen_y))
    
    def get_cell_from_mouse(self, pos):
        """
        Перетворює координати миші на координати клітинки дошки
        
        Args:
            pos (tuple): Координати миші (x, y)
        
        Returns:
            tuple: Координати клітинки (x, y) в діапазоні 1-8
        """
        x, y = pos
        cell_x = x // CELL_SIZE + 1
        cell_y = y // CELL_SIZE + 1
        return cell_x, cell_y
    
    def get_possible_moves(self, x, y):
        """
        Отримує всі можливі ходи для шашки на позиції (x, y)
        
        Args:
            x (int): Координата X (1-8)
            y (int): Координата Y (1-8)
        
        Returns:
            list: Список координат (x, y) можливих ходів
        """
        possible_moves = []
        piece = self.interface.get_piece(self.board, x, y)
        
        # Спочатку перевіряємо всі можливі взяття
        # Для дамок потрібно перевірити більше діагоналей
        if piece in ["wk", "bk"]:
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    # Перевіряємо всі діагональні напрямки
                    for dist in range(1, 8):
                        to_x = x + dx * dist
                        to_y = y + dy * dist
                        if 1 <= to_x <= 8 and 1 <= to_y <= 8:
                            if self.interface.is_valid_capture(self.board, x, y, to_x, to_y, self.current_player):
                                possible_moves.append((to_x, to_y))
   
        else:
            # Для звичайних шашок перевіряємо тільки взяття на відстань 2
            for dir_x in [-2, 2]:
                for dir_y in [-2, 2]:
                    to_x = x + dir_x
                    to_y = y + dir_y
                    if 1 <= to_x <= 8 and 1 <= to_y <= 8:
                        if self.interface.is_valid_capture(self.board, x, y, to_x, to_y, self.current_player):
                            possible_moves.append((to_x, to_y))
        
        # Якщо немає можливих взять, перевіряємо звичайні ходи
        if not possible_moves:
            if piece in ["wk", "bk"]:
                for dx in [-1, 1]:
                    for dy in [-1, 1]:
                        for dist in range(1, 8):
                            to_x = x + dx * dist
                            to_y = y + dy * dist
                            if 1 <= to_x <= 8 and 1 <= to_y <= 8:
                                if self.interface.is_valid_king_move(self.board, x, y, to_x, to_y, self.current_player):
                                    possible_moves.append((to_x, to_y))
            else:
                # Звичайні шашки можуть рухатись тільки на 1 клітинку
                for dir_x in [-1, 1]:
                    # Білі рухаються вгору (y-1), чорні — вниз (y+1)
                    dir_y = -1 if self.current_player == "white" else 1
                    to_x = x + dir_x
                    to_y = y + dir_y
                    if 1 <= to_x <= 8 and 1 <= to_y <= 8:
                        if self.interface.is_valid_move(self.board, x, y, to_x, to_y, self.current_player):
                            possible_moves.append((to_x, to_y))
        
        return possible_moves
    
    def handle_click(self, pos):
        """
        Обробляє клік миші
        
        Args:
            pos (tuple): Координати кліку миші (x, y)
        """
        if self.game_over:
            return
        
        x, y = self.get_cell_from_mouse(pos)
        
        # Перевіряємо, чи клітинка знаходиться в межах дошки
        if not (1 <= x <= 8 and 1 <= y <= 8):
            return
        
        # Якщо шашка ще не вибрана
        if not self.selected_piece:
            piece = self.interface.get_piece(self.board, x, y)
            # Перевіряємо, чи це шашка поточного гравця
            if piece != "empty" and ((piece == "w" or piece == "wk") and self.current_player == "white" or
                                   (piece == "b" or piece == "bk") and self.current_player == "black"):
                self.selected_piece = (x, y)
                self.possible_moves = self.get_possible_moves(x, y)
        else:
            # Якщо шашка вже вибрана, намагаємося зробити хід
            from_x, from_y = self.selected_piece
            to_x, to_y = x, y 
            if (x, y) in self.possible_moves:
                # Виконуємо хід
                new_board = self.interface.make_move(self.board, from_x, from_y, to_x, to_y, self.current_player)
                if new_board:
                    self.board = new_board
                    
                    # Перевіряємо, чи було взяття
                    was_capture = abs(to_x - from_x) == 2 and abs(to_y - from_y) == 2
                    
                    # Якщо було взяття, перевіряємо можливість додаткових взять
                    if was_capture:
                        additional_captures = self.get_possible_moves(to_x, to_y)
                        captures_only = []
                        for move in additional_captures:
                            addl_to_x, addl_to_y = move
                            if abs(addl_to_x - to_x) == 2 and abs(addl_to_y - to_y) == 2:
                                captures_only.append(move)
                        
                        if captures_only:
                            # Якщо є додаткові взяття, вибираємо нову позицію
                            self.selected_piece = (to_x, to_y)
                            self.possible_moves = captures_only
                            return
                    
                    # Перемикаємо гравця, якщо не було взяття або немає додаткових взять
                    self.current_player = "black" if self.current_player == "white" else "white"
            
            # Скидаємо виділення
            self.selected_piece = None
            self.possible_moves = []
    
    def check_game_over(self):
        """
        Перевіряє, чи гра закінчена
        
        Returns:
            bool: True, якщо гра закінчена, інакше False
        """
        # Перевіряємо, чи у поточного гравця є можливі ходи
        for x in range(1, 9):
            for y in range(1, 9):
                piece = self.interface.get_piece(self.board, x, y)
                is_player_piece = False
                if self.current_player == "white" and (piece == "w" or piece == "wk"):
                    is_player_piece = True
                elif self.current_player == "black" and (piece == "b" or piece == "bk"):
                    is_player_piece = True
                
                if is_player_piece and self.get_possible_moves(x, y):
                    return False
        
        # Якщо немає можливих ходів, гра закінчена
        return True
    
    def show_game_over(self):
        """
        Показує повідомлення про закінчення гри
        """
        winner = "black" if self.current_player == "white" else "white"
        font = pygame.font.SysFont('Arial', 36)
        text = font.render(f"Гра закінчена! Переміг {winner}!", True, RED)
        text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
        
        # Створюємо напівпрозорий фон
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text, text_rect)
        
        # Додаємо повідомлення про перезапуск
        restart_font = pygame.font.SysFont('Arial', 24)
        restart_text = restart_font.render("Натисніть 'R' для перезапуску", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def show_current_player(self):
        """
        Показує поточного гравця
        """
        font = pygame.font.SysFont('Arial', 20)
        text = font.render(f"Хід: {'білих' if self.current_player == 'white' else 'чорних'}", True, BLACK)
        text_rect = text.get_rect(topleft=(10, 10))
        
        # Білий фон для тексту
        pygame.draw.rect(self.screen, WHITE, (5, 5, text.get_width() + 10, text.get_height() + 10))
        self.screen.blit(text, text_rect)
    
    def reset_game(self):
        """
        Скидає гру до початкового стану
        """
        self.board = self.interface.get_initial_board()
        self.current_player = "white"
        self.selected_piece = None
        self.possible_moves = []
        self.game_over = False
    
    def run(self):
        """
        Основний цикл гри
        """
        running = True
        while running:
            # Обробка подій
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Лівий клік миші
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Кнопка R для перезапуску
                        self.reset_game()
            
            # Перевірка закінчення гри
            if not self.game_over:
                self.game_over = self.check_game_over()
            
            # Малювання дошки
            self.draw_board()
            
            # Підсвічування вибраної шашки та можливих ходів
            self.highlight_selected()
            
            # Малювання шашок
            self.draw_pieces()
            
            # Показуємо поточного гравця
            self.show_current_player()
            
            # Показуємо повідомлення про закінчення гри, якщо гра закінчена
            if self.game_over:
                self.show_game_over()
            
            # Оновлення екрану
            pygame.display.flip()
            
            # Обмеження частоти кадрів
            self.clock.tick(60)
        
        # Завершення роботи PyGame
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # Створюємо та запускаємо графічний інтерфейс
    gui = CheckersGUI()
    gui.run()
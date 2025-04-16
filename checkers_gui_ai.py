import pygame
import sys
import time
from checkers_interface import CheckersInterface
from checkers_ai import CheckersAI

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

class CheckersGUIAI:
    """
    Графічний інтерфейс користувача для гри в шашки проти AI з використанням PyGame
    """
    def __init__(self, difficulty="medium"):
        """
        Ініціалізація графічного інтерфейсу
        
        Args:
            difficulty (str): Рівень складності AI ('easy', 'medium', 'hard')
        """
        # Ініціалізація PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption(f"Шашки проти AI (Складність: {difficulty})")
        
        # Логіка гри
        self.interface = CheckersInterface()
        self.board = self.interface.get_initial_board()
        self.ai = CheckersAI(difficulty)
        
        # Гравець завжди грає за білих, AI за чорних
        self.current_player = "white"
        
        # Змінні стану гри
        self.selected_piece = None
        self.possible_moves = []
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
        
        # Завантаження та масштабування зображень шашок
        self.images = {
            'w': self._scale_image('assets/white_checker.png'),
            'b': self._scale_image('assets/black_checker.png'),
            'wk': self._scale_image('assets/white_king.png'),
            'bk': self._scale_image('assets/black_king.png')
        }
        
        # Таймер для оновлення екрану
        self.clock = pygame.time.Clock()
        
        # Додаємо кнопку "Нова гра"
        self.new_game_button = pygame.Rect(WINDOW_SIZE // 2 - 75, WINDOW_SIZE - 40, 150, 30)
        
        # Додаємо селектор складності
        self.difficulties = ["easy", "medium", "hard"]
        self.current_difficulty = self.difficulties.index(difficulty)
        self.difficulty_buttons = []
        for i, diff in enumerate(self.difficulties):
            button_width = 80
            button_x = 20 + i * (button_width + 10)
            self.difficulty_buttons.append(pygame.Rect(button_x, WINDOW_SIZE - 40, button_width, 30))
    
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
        
        # Перевіряємо всі можливі ходи
        for to_x in range(1, 9):
            for to_y in range(1, 9):
                # Спочатку перевіряємо взяття
                if self.interface.is_valid_capture(self.board, x, y, to_x, to_y, self.current_player):
                    possible_moves.append((to_x, to_y))
        
        # Якщо немає можливих взять, перевіряємо звичайні ходи
        if not possible_moves:
            for to_x in range(1, 9):
                for to_y in range(1, 9):
                    if self.interface.is_valid_move(self.board, x, y, to_x, to_y, self.current_player):
                        possible_moves.append((to_x, to_y))
        
        return possible_moves
    
    def handle_click(self, pos):
        """
        Обробляє клік миші
        
        Args:
            pos (tuple): Координати кліку миші (x, y)
        """
        # Перевіряємо, чи клікнуто на кнопку "Нова гра"
        if self.new_game_button.collidepoint(pos):
            self.reset_game()
            return
        
        # Перевіряємо, чи клікнуто на кнопки складності
        for i, button in enumerate(self.difficulty_buttons):
            if button.collidepoint(pos):
                self.current_difficulty = i
                self.ai = CheckersAI(self.difficulties[i])
                pygame.display.set_caption(f"Шашки проти AI (Складність: {self.difficulties[i]})")
                self.reset_game()
                return
        
        # Якщо гра закінчена або AI думає, ігноруємо кліки на дошці
        if self.game_over or self.ai_thinking or self.current_player != "white":
            return
        
        x, y = self.get_cell_from_mouse(pos)
        
        # Перевіряємо, чи клітинка знаходиться в межах дошки
        if not (1 <= x <= 8 and 1 <= y <= 8):
            return
        
        # Якщо шашка ще не вибрана
        if not self.selected_piece:
            piece = self.interface.get_piece(self.board, x, y)
            # Перевіряємо, чи це шашка гравця (білі)
            if piece == "w" or piece == "wk":
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
                    
                    # Перевіряємо чи закінчилася гра після ходу гравця
                    if self.check_game_over("black"):
                        self.game_over = True
                        self.winner = "white"
                        return
                    
                    # Перемикаємо гравця на AI
                    self.current_player = "black"
                    
                    # Скидаємо виділення
                    self.selected_piece = None
                    self.possible_moves = []
                    
                    # Запускаємо хід AI з невеликою затримкою
                    self.ai_thinking = True
            else:
                # Скидаємо виділення, якщо клікнули на недозволене місце
                self.selected_piece = None
                self.possible_moves = []
    
    def ai_make_move(self):
        """
        Виконує хід AI
        """
        # Симулюємо "роздуми" AI для кращого UX (коротка пауза)
        pygame.display.flip()
        time.sleep(0.5)
        
        # AI робить хід
        new_board, move = self.ai.make_move(self.board)
        
        if new_board is not None:
            self.board = new_board
            
            # Перевіряємо чи закінчилася гра після ходу AI
            if self.check_game_over("white"):
                self.game_over = True
                self.winner = "black"
            else:
                # Перемикаємо гравця назад на людину
                self.current_player = "white"
        else:
            # Якщо AI не може зробити хід, гра закінчена
            self.game_over = True
            self.winner = "white"
        
        self.ai_thinking = False
    
    def check_game_over(self, player_to_check):
        return False
    
    def draw_buttons(self):
        """
        Малює кнопки інтерфейсу
        """
        # Малюємо кнопку "Нова гра"
        pygame.draw.rect(self.screen, BLUE, self.new_game_button)
        pygame.draw.rect(self.screen, BLACK, self.new_game_button, 2)
        
        font = pygame.font.SysFont('Arial', 18)
        text = font.render("Нова гра", True, WHITE)
        text_rect = text.get_rect(center=self.new_game_button.center)
        self.screen.blit(text, text_rect)
        
        # Малюємо кнопки складності
        difficulty_names = ["Легкий", "Середній", "Складний"]
        for i, button in enumerate(self.difficulty_buttons):
            # Поточний рівень складності виділяємо іншим кольором
            color = GREEN if i == self.current_difficulty else DARK_BROWN
            pygame.draw.rect(self.screen, color, button)
            pygame.draw.rect(self.screen, BLACK, button, 2)
            
            font = pygame.font.SysFont('Arial', 16)
            text = font.render(difficulty_names[i], True, WHITE)
            text_rect = text.get_rect(center=button.center)
            self.screen.blit(text, text_rect)
    
    def show_game_over(self):
        """
        Показує повідомлення про закінчення гри
        """
        winner_text = "Ви перемогли!" if self.winner == "white" else "AI переміг!"
        font = pygame.font.SysFont('Arial', 36)
        text = font.render(f"Гра закінчена! {winner_text}", True, RED)
        text_rect = text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
        
        # Створюємо напівпрозорий фон
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text, text_rect)
        
        # Додаємо повідомлення про перезапуск
        restart_font = pygame.font.SysFont('Arial', 24)
        restart_text = restart_font.render("Натисніть 'R' для перезапуску або клікніть 'Нова гра'", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def show_current_player(self):
        """
        Показує поточного гравця
        """
        font = pygame.font.SysFont('Arial', 20)
        
        if self.ai_thinking:
            text = font.render("AI думає...", True, BLACK)
        else:
            text = font.render(f"Хід: {'ваш' if self.current_player == 'white' else 'AI'}", True, BLACK)
        
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
        self.winner = None
        self.ai_thinking = False
    
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
            
            # Малювання дошки
            self.draw_board()
            
            # Підсвічування вибраної шашки та можливих ходів
            self.highlight_selected()
            
            # Малювання шашок
            self.draw_pieces()
            
            # Малюємо кнопки
            self.draw_buttons()
            
            # Показуємо поточного гравця
            self.show_current_player()
            
            # Якщо зараз хід AI і гра не закінчена
            if self.current_player == "black" and not self.game_over and not self.ai_thinking:
                self.ai_thinking = True
            
            # Якщо AI думає, робимо хід
            if self.ai_thinking and not self.game_over:
                self.ai_make_move()
            
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
    gui = CheckersGUIAI(difficulty="medium")
    gui.run()
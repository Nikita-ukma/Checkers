import pygame
import sys
from checkers_gui import CheckersGUI
from checkers_gui_ai import CheckersGUIAI
# Константи
WINDOW_SIZE = 800
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_BROWN = (139, 69, 19)
LIGHT_BROWN = (222, 184, 135)
BUTTON_COLOR = (70, 130, 180)  # Сталевий синій
BUTTON_HOVER_COLOR = (100, 149, 237)  # Синій колір при наведенні

class GameMenu:
    """
    Головне меню гри в шашки
    """
    def __init__(self):
        """
        Ініціалізація меню
        """
        # Ініціалізація PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Шашки - Головне меню")
        
        # Завантажуємо фонове зображення
        try:
            self.background = pygame.image.load('assets/menu_background.png')
            self.background = pygame.transform.scale(self.background, (WINDOW_SIZE, WINDOW_SIZE))
        except pygame.error:
            self.background = None
            print("Не вдалося завантажити фонове зображення. Використовуємо фон за замовчуванням.")
        
        # Шрифти
        self.title_font = pygame.font.SysFont('Arial', 72, bold=True)
        self.button_font = pygame.font.SysFont('Arial', 36)
        
        # Кнопки меню
        self.buttons = [
            {
                'text': 'Гравець проти гравця',
                'rect': pygame.Rect(WINDOW_SIZE // 2 - 200, WINDOW_SIZE // 2, 400, 60),
                'action': self.start_pvp_game
            },
            {
                'text': 'Гравець проти комп\'ютера',
                'rect': pygame.Rect(WINDOW_SIZE // 2 - 200, WINDOW_SIZE // 2 + 100, 400, 60),
                'action': self.start_pve_game
            },
            {
                'text': 'Вихід',
                'rect': pygame.Rect(WINDOW_SIZE // 2 - 200, WINDOW_SIZE // 2 + 200, 400, 60),
                'action': self.exit_game
            }
        ]
        
        # Таймер для оновлення екрану
        self.clock = pygame.time.Clock()
    
    def draw_menu(self):
        """
        Малює головне меню
        """
        # Малюємо фон
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # Малюємо шаховий фон, якщо немає зображення
            for row in range(8):
                for col in range(8):
                    if (row + col) % 2 == 0:
                        color = LIGHT_BROWN
                    else:
                        color = DARK_BROWN
                    pygame.draw.rect(self.screen, color, (col * WINDOW_SIZE // 8, row * WINDOW_SIZE // 8, 
                                                         WINDOW_SIZE // 8, WINDOW_SIZE // 8))
        
        # Малюємо заголовок
        title = self.title_font.render("ШАШКИ", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 4))
        
        # Додаємо тінь для кращої видимості
        title_shadow = self.title_font.render("ШАШКИ", True, BLACK)
        title_shadow_rect = title_shadow.get_rect(center=(WINDOW_SIZE // 2 + 4, WINDOW_SIZE // 4 + 4))
        self.screen.blit(title_shadow, title_shadow_rect)
        self.screen.blit(title, title_rect)
        
        # Малюємо кнопки
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            # Перевіряємо, чи наведено курсор на кнопку
            if button['rect'].collidepoint(mouse_pos):
                color = BUTTON_HOVER_COLOR
            else:
                color = BUTTON_COLOR
            
            # Малюємо кнопку
            pygame.draw.rect(self.screen, color, button['rect'], border_radius=15)
            pygame.draw.rect(self.screen, BLACK, button['rect'], 2, border_radius=15)
            
            # Малюємо текст на кнопці
            text = self.button_font.render(button['text'], True, WHITE)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
    
    def handle_events(self):
        """
        Обробляє події PyGame
        
        Returns:
            bool: True, якщо гра продовжується, False, якщо слід вийти
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Лівий клік миші
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self.buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            button['action']()
                            return True
        return True
    
    def start_pvp_game(self):
        """
        Запускає гру в режимі гравець проти гравця
        """
        # Закриваємо меню та запускаємо гру
        pygame.quit()
        game = CheckersGUI()
        game.run()
    
    def start_pve_game(self):
        pygame.quit()
        game = CheckersGUIAI()
        game.run()
        
        # Поки що просто виводимо повідомлення
        print("Режим гравець проти комп'ютера буде доданий пізніше.")
    
    def exit_game(self):
        """
        Виходить з гри
        """
        pygame.quit()
        sys.exit()
    
    def run(self):
        """
        Основний цикл меню
        """
        running = True
        while running:
            # Обробка подій
            running = self.handle_events()
            
            # Малювання меню
            self.draw_menu()
            
            # Оновлення екрану
            pygame.display.flip()
            
            # Обмеження частоти кадрів
            self.clock.tick(60)
        
        # Завершення роботи PyGame
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # Запускаємо меню
    menu = GameMenu()
    menu.run()
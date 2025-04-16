# Файл: test_gui.py
import unittest
import pygame
import os
import sys
from unittest.mock import MagicMock, patch
from checkers_gui import CheckersGUI

class TestCheckersGUI(unittest.TestCase):
    """
    Клас для тестування графічного інтерфейсу гри в шашки
    """
    @classmethod
    def setUpClass(cls):
        """
        Налаштування середовища перед усіма тестами
        """
        # Ініціалізація PyGame перед тестуванням
        os.environ['SDL_VIDEODRIVER'] = 'dummy'  # Використовуємо фіктивний драйвер для тестування
        pygame.init()
    
    def setUp(self):
        """
        Підготовка тестового середовища перед кожним тестом
        """
        # Налаштування мокованого графічного інтерфейсу
        with patch('pygame.display.set_mode'):
            with patch('checkers_interface.CheckersInterface'):
                self.gui = CheckersGUI()
                # Мокуємо інтерфейс
                self.gui.interface = MagicMock()
                # Створюємо тестову дошку
                self.gui.board = [
                    ["empty" for _ in range(8)] for _ in range(8)
                ]
                # Додаємо кілька фігур для тестування
                self.gui.board[0][1] = "b"
                self.gui.board[5][0] = "w"
    
    def test_get_cell_from_mouse(self):
        """
        Тестує перетворення координат миші в координати клітинки
        """
        # Тестуємо різні координати миші
        cell = self.gui.get_cell_from_mouse((50, 50))
        self.assertEqual(cell, (1, 1), "Координати миші (50, 50) повинні відповідати клітинці (1, 1)")
        
        cell = self.gui.get_cell_from_mouse((150, 250))
        self.assertEqual(cell, (2, 3), "Координати миші (150, 250) повинні відповідати клітинці (2, 3)")
        
        cell = self.gui.get_cell_from_mouse((799, 799))
        self.assertEqual(cell, (8, 8), "Координати миші (799, 799) повинні відповідати клітинці (8, 8)")
    
    def test_get_possible_moves(self):
        """
        Тестує отримання можливих ходів
        """
        # Мокуємо метод is_valid_move
        self.gui.interface.is_valid_move.return_value = True
        self.gui.interface.is_valid_capture.return_value = False
        
        # Отримуємо можливі ходи
        moves = self.gui.get_possible_moves(1, 1)
        self.assertEqual(len(moves), 64, "При відсутності обмежень повинно бути 64 можливі ходи")
        
        # Тестуємо з мокованими обмеженнями
        def mock_is_valid_move(board, from_x, from_y, to_x, to_y, player):
            # Імітуємо правила ходу в шашках - тільки по діагоналі
            return abs(to_x - from_x) == 1 and abs(to_y - from_y) == 1
        
        self.gui.interface.is_valid_move.side_effect = mock_is_valid_move
        
        moves = self.gui.get_possible_moves(4, 4)
        self.assertEqual(len(moves), 4, "Повинно бути 4 можливі ходи для шашки в центрі дошки")
        
        # Перевіряємо правильність ходів
        expected_moves = [(3, 3), (3, 5), (5, 3), (5, 5)]
        for move in expected_moves:
            self.assertIn(move, moves, f"Хід {move} повинен бути серед можливих")
    
    def test_reset_game(self):
        """
        Тестує функцію перезапуску гри
        """
        # Змінюємо стан гри
        self.gui.current_player = "black"
        self.gui.selected_piece = (1, 1)
        self.gui.possible_moves = [(2, 2), (3, 3)]
        self.gui.game_over = True
        
        # Мокуємо метод get_initial_board
        self.gui.interface.get_initial_board.return_value = [["empty" for _ in range(8)] for _ in range(8)]
        
        # Перезапускаємо гру
        self.gui.reset_game()
        
        # Перевіряємо, що стан гри скинуто
        self.assertEqual(self.gui.current_player, "white", "Після перезапуску має ходити білий гравець")
        self.assertIsNone(self.gui.selected_piece, "Після перезапуску не повинно бути вибраної шашки")
        self.assertEqual(self.gui.possible_moves, [], "Після перезапуску не повинно бути можливих ходів")
        self.assertFalse(self.gui.game_over, "Після перезапуску гра не повинна бути завершена")
    
    def test_check_game_over(self):
        """
        Тестує функцію перевірки закінчення гри
        """
        # Мокуємо метод get_piece та get_possible_moves
        self.gui.interface.get_piece.return_value = "w"
        self.gui.get_possible_moves = MagicMock(return_value=[(2, 2)])
        
        # Перевіряємо гру, коли є можливі ходи
        self.assertFalse(self.gui.check_game_over(), "Гра не повинна бути завершена, якщо є можливі ходи")
        
        # Змінюємо мок, щоб не було можливих ходів
        self.gui.get_possible_moves = MagicMock(return_value=[])
        
        # Перевіряємо гру, коли немає можливих ходів
        self.assertTrue(self.gui.check_game_over(), "Гра повинна бути завершена, якщо немає можливих ходів")
    
    def test_handle_click_select_piece(self):
        """
        Тестує обробку кліку для вибору шашки
        """
        # Мокуємо метод get_piece
        self.gui.interface.get_piece.return_value = "w"
        self.gui.get_possible_moves = MagicMock(return_value=[(2, 2)])
        
        # Обробляємо клік по білій шашці
        self.gui.handle_click((50, 50))  # Клік на позиції (1, 1)
        
        # Перевіряємо, що шашка вибрана
        self.assertEqual(self.gui.selected_piece, (1, 1), "Після кліку на шашку, вона повинна бути вибрана")
        self.assertEqual(self.gui.possible_moves, [(2, 2)], "Після вибору шашки повинні бути показані можливі ходи")
    
    def test_handle_click_move_piece(self):
        """
        Тестує обробку кліку для переміщення шашки
        """
        # Налаштовуємо стан перед переміщенням
        self.gui.selected_piece = (1, 1)
        self.gui.possible_moves = [(2, 2)]
        self.gui.current_player = "white"
        
        # Мокуємо метод make_move
        self.gui.interface.make_move.return_value = [["empty" for _ in range(8)] for _ in range(8)]
        
        # Обробляємо клік по можливому ходу
        self.gui.handle_click((150, 150))  # Клік на позиції (2, 2)
        
        # Перевіряємо, що хід виконано
        self.gui.interface.make_move.assert_called_once()
        self.assertIsNone(self.gui.selected_piece, "Після ходу не повинно бути вибраної шашки")
        self.assertEqual(self.gui.possible_moves, [], "Після ходу не повинно бути можливих ходів")
        self.assertEqual(self.gui.current_player, "black", "Після ходу має ходити інший гравець")


def run_tests():
    """
    Запускає тести графічного інтерфейсу
    """
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == "__main__":
    run_tests()
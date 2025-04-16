import unittest
import pygame
from unittest.mock import Mock, patch
from checkers_interface import CheckersInterface
from checkers_gui_ai import CheckersGUIAI

class TestCheckersGUIAI(unittest.TestCase):
    def setUp(self):
        # Ініціалізуємо pygame для тестування
        pygame.init()
        # Створюємо макет для екрану
        pygame.display.set_mode = Mock(return_value=pygame.Surface((800, 800)))
        # Ініціалізуємо гру
        self.game = CheckersGUIAI(difficulty="easy")
        # Створюємо доступ до інтерфейсу для перевірок
        self.interface = self.game.interface

    def tearDown(self):
        pygame.quit()
    
    def test_initial_board_setup(self):
        """Перевірка правильної ініціалізації дошки"""
        board = self.game.board
        # Перевіряємо наявність білих шашок внизу (3 рядки)
        for row in range(6, 9):
            for col in range(1, 9):
                if (row + col) % 2 != 0:  # Тільки на темних клітинках
                    piece = self.interface.get_piece(board, col, row)
                    self.assertIn(piece, ["w", "empty"], 
                                 f"Неправильна шашка на {col}, {row}: {piece}")
        
        # Перевіряємо наявність чорних шашок вгорі (3 рядки)
        for row in range(1, 4):
            for col in range(1, 9):
                if (row + col) % 2 != 0:  # Тільки на темних клітинках
                    piece = self.interface.get_piece(board, col, row)
                    self.assertIn(piece, ["b", "empty"], 
                                 f"Неправильна шашка на {col}, {row}: {piece}")
    
    def test_get_possible_moves(self):
        """Тест на правильне визначення можливих ходів"""
        # Встановлюємо тестову дошку з відомою конфігурацією
        test_board = self.interface.get_initial_board()
        # Перевіряємо наявність хоча б одного можливого ходу для білої шашки
        self.game.board = test_board
        self.game.current_player = "white"
        
        # Шашки в початковій позиції мають мати можливі ходи
        # 3, 6 - це координати білої шашки в 3-му стовпчику на 6-му рядку
        possible_moves = self.game.get_possible_moves(3, 6)
        
        # Виводимо дошку для діагностики
        self._print_board(test_board)
        
        # У початковій позиції мають бути можливі ходи
        self.assertTrue(len(possible_moves) > 0, 
                       f"Не знайдено можливих ходів для шашки на 3,6. Можливі ходи: {possible_moves}")
    
    def test_handling_piece_selection(self):
        """Тест на правильну обробку вибору шашки"""
        # Симулюємо клік по шашці
        self.game.current_player = "white"
        self.game.game_over = False
        
        # Симулюємо клік на білу шашку на позиції (3, 6)
        x, y = 3, 6
        screen_x = (x - 1) * (800 // 8) + (800 // 16)  # Центр клітинки
        screen_y = (y - 1) * (800 // 8) + (800 // 16)
        
        # Отримуємо шашку в цій позиції
        piece = self.interface.get_piece(self.game.board, x, y)
        print(f"Шашка на позиції {x},{y}: {piece}")
        
        # Зберігаємо поточний стан гри
        self.game.handle_click((screen_x, screen_y))
        
        # Перевіряємо, що шашка була вибрана
        self.assertEqual(self.game.selected_piece, (x, y), 
                        f"Шашка не була вибрана. selected_piece = {self.game.selected_piece}")
        
        # Перевіряємо, що гра не закінчилася після вибору шашки
        self.assertFalse(self.game.game_over, "Гра закінчилася після вибору шашки")
    
    def test_valid_move_detection(self):
        """Тест на визначення валідних ходів"""
        # Створюємо дошку з відомою конфігурацією
        test_board = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                test_board[row][col] = "empty"
        
        # Додаємо білу шашку і порожні клітинки для ходу
        test_board[5][2] = "w"  # Позиція 3,6
        test_board[4][1] = "empty"  # Позиція 2,5 (можливий хід)
        test_board[4][3] = "empty"  # Позиція 4,5 (можливий хід)
        
        self.game.board = test_board
        self.game.current_player = "white"
        
        # Перевіряємо наявність можливих ходів
        moves = self.game.get_possible_moves(3, 6)
        self.assertIn((2, 5), moves, "Хід на 2,5 повинен бути можливим")
        self.assertIn((4, 5), moves, "Хід на 4,5 повинен бути можливим")
    
    def _print_board(self, board):
        """Виводить дошку в консоль для діагностики"""
        print("\nПоточна дошка:")
        for row in range(8):
            row_str = ""
            for col in range(8):
                piece = self.interface.get_piece(board, col+1, row+1)
                if piece == "empty":
                    row_str += ". "
                else:
                    row_str += piece + " "
            print(f"{8-row} {row_str}")
        
        print("  a b c d e f g h")

if __name__ == "__main__":
    unittest.main()
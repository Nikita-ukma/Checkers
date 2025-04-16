# Файл: test_interface.py
import unittest
import CheckersInterface

class TestCheckersInterface(unittest.TestCase):
    """
    Клас для тестування інтерфейсу між Prolog і Python
    """
    def setUp(self):
        """
        Підготовка тестового середовища
        """
        self.interface = CheckersInterface()
        self.initial_board = self.interface.get_initial_board()
        self.empty_board = self.interface.get_empty_board()
    
    def test_get_initial_board(self):
        """
        Тестування отримання початкової дошки
        """
        board = self.initial_board
        self.assertEqual(len(board), 8, "Дошка повинна мати 8 рядків")
        self.assertEqual(len(board[0]), 8, "Кожен рядок повинен мати 8 клітинок")
        # Перевіряємо, що фігури знаходяться на правильних місцях
        self.assertEqual(board[0][1], "b", "На позиції (2,1) має бути чорна шашка")
        self.assertEqual(board[5][0], "w", "На позиції (1,6) має бути біла шашка")
    
    def test_get_empty_board(self):
        """
        Тестування отримання порожньої дошки
        """
        board = self.empty_board
        self.assertEqual(len(board), 8, "Дошка повинна мати 8 рядків")
        self.assertEqual(len(board[0]), 8, "Кожен рядок повинен мати 8 клітинок")
        # Перевіряємо, що всі клітинки порожні
        for row in board:
            for cell in row:
                self.assertEqual(cell, "empty", "Всі клітинки порожньої дошки мають бути 'empty'")
    
    def test_get_piece(self):
        """
        Тестування отримання фігури
        """
        piece = self.interface.get_piece(self.initial_board, 1, 6)
        self.assertEqual(piece, "w", "На позиції (1,6) має бути біла шашка")
        
        piece = self.interface.get_piece(self.initial_board, 2, 1)
        self.assertEqual(piece, "b", "На позиції (2,1) має бути чорна шашка")
        
        piece = self.interface.get_piece(self.initial_board, 1, 4)
        self.assertEqual(piece, "empty", "На позиції (1,4) не має бути фігури")
    
    def test_is_valid_move(self):
        """
        Тестування перевірки допустимого ходу
        """
        # Допустимий хід білою шашкою
        self.assertTrue(self.interface.is_valid_move(self.initial_board, 1, 6, 2, 5, "white"),
                        "Хід (1,6) -> (2,5) білою шашкою має бути допустимим")
        
        # Недопустимий хід білою шашкою (через 2 клітинки)
        self.assertFalse(self.interface.is_valid_move(self.initial_board, 1, 6, 3, 4, "white"),
                        "Хід (1,6) -> (3,4) білою шашкою має бути недопустимим")
        
        # Недопустимий хід чорною шашкою (не по діагоналі)
        self.assertFalse(self.interface.is_valid_move(self.initial_board, 2, 1, 2, 2, "black"),
                        "Хід (2,1) -> (2,2) чорною шашкою має бути недопустимим")
    
    def test_make_move(self):
        """
        Тестування виконання ходу
        """
        # Виконуємо правильний хід
        new_board = self.interface.make_move(self.initial_board, 1, 6, 2, 5, "white")
        self.assertIsNotNone(new_board, "Результат правильного ходу не повинен бути None")
        # Перевіряємо, що фігура перемістилася
        self.assertEqual(new_board[5][0], "empty", "Початкова позиція має бути порожньою")
        self.assertEqual(new_board[4][1], "w", "Кінцева позиція має містити білу шашку")
        
        # Намагаємося виконати неправильний хід
        invalid_board = self.interface.make_move(self.initial_board, 1, 6, 3, 4, "white")
        self.assertIsNone(invalid_board, "Результат неправильного ходу має бути None")
    
    def test_is_valid_capture(self):
        """
        Тестування перевірки допустимого взяття
        """
        # Створюємо дошку для тестування взяття
        test_board = self.empty_board
        board_with_capture = []
        for row in test_board:
            board_with_capture.append(row.copy())
        
        # Розміщуємо фігури для взяття
        board_with_capture[4][2] = "w"  # Біла шашка на (3,5)
        board_with_capture[3][3] = "b"  # Чорна шашка на (4,4)
        
        # Взяття має бути можливим
        self.assertTrue(self.interface.is_valid_capture(board_with_capture, 3, 5, 5, 3, "white"),
                        "Взяття (3,5) -> (5,3) має бути допустимим")
        
        # Неправильне взяття (немає фігури для взяття)
        self.assertFalse(self.interface.is_valid_capture(self.initial_board, 1, 6, 3, 4, "white"),
                        "Взяття (1,6) -> (3,4) має бути недопустимим, оскільки немає фігури для взяття")


def run_tests():
    """
    Запускає тести інтерфейсу
    """
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == "__main__":
    run_tests()
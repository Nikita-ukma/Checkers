# Файл: checkers_interface.py
from pyswip import Prolog
import numpy as np

class CheckersInterface:
    """
    Клас для інтерфейсу між Python і Prolog для гри в шашки
    """
    def __init__(self, prolog_file="checkers.pl"):
        try:
            self.prolog = Prolog()
            # Збільшимо стек для SWI-Prolog
            self.prolog.query("set_prolog_flag(stack_limit, 32_000_000)")
            self.prolog.query("set_prolog_flag(toplevel_print_options, [quoted(true), portray(true), max_depth(100)])")
            self.prolog.consult(prolog_file)
            print("Prolog initialized successfully")
        except Exception as e:
            print(f"Помилка ініціалізації Prolog: {e}")
            raise
    
    def _board_prolog_to_python(self, prolog_board):
        """
        Конвертує представлення дошки з Prolog у Python (список списків)
        
        Args:
            prolog_board: Представлення дошки у форматі Prolog
            
        Returns:
            list: Дошка у форматі Python (список списків)
        """
        # Перетворення Prolog-терміну в Python-структуру даних
        python_board = []
        for row in prolog_board:
            python_row = []
            for cell in row:
                # Конвертуємо Prolog атоми в Python рядки
                python_row.append(str(cell))
            python_board.append(python_row)
        return python_board
    
    def _board_python_to_prolog(self, python_board):
        """
        Конвертує представлення дошки з Python у Prolog-термін
        
        Args:
            python_board (list): Дошка у форматі Python
            
        Returns:
            str: Prolog-термін для представлення дошки
        """
        prolog_board = "["
        for i, row in enumerate(python_board):
            if i > 0:
                prolog_board += ","
            prolog_board += "["
            for j, cell in enumerate(row):
                if j > 0:
                    prolog_board += ","
                # Конвертуємо Python рядки в Prolog атоми
                prolog_board += cell
            prolog_board += "]"
        prolog_board += "]"
        return prolog_board
    
    def get_initial_board(self):
        """
        Отримує початкову позицію дошки з Prolog
        
        Returns:
            list: Початкова дошка у форматі Python
        """
        result = list(self.prolog.query("initial_board(Board)"))
        if result:
            return self._board_prolog_to_python(result[0]["Board"])
        else:
            raise Exception("Не вдалося отримати початкову дошку")
    
    def get_empty_board(self):
        """
        Отримує порожню дошку з Prolog
        
        Returns:
            list: Порожня дошка у форматі Python
        """
        result = list(self.prolog.query("empty_board(Board)"))
        if result:
            return self._board_prolog_to_python(result[0]["Board"])
        else:
            raise Exception("Не вдалося отримати порожню дошку")
    
    def get_piece(self, board, x, y):
        """
        Отримує фігуру на вказаній позиції
        
        Args:
            board (list): Поточна дошка
            x (int): Координата X (1-8)
            y (int): Координата Y (1-8)
        
        Returns:
            str: Фігура на вказаній позиції ('empty', 'w', 'b', 'wk', 'bk')
        """
        board_term = self._board_python_to_prolog(board)
        query = f"get_piece({board_term}, {x}, {y}, Piece)"
        result = list(self.prolog.query(query))
        if result:
            return str(result[0]["Piece"])
        else:
            raise Exception(f"Не вдалося отримати фігуру на позиції ({x}, {y})")
    
    def is_valid_move(self, board, from_x, from_y, to_x, to_y, player):
        """
        Перевіряє, чи є хід допустимим
        
        Args:
            board (list): Поточна дошка
            from_x (int): Початкова координата X (1-8)
            from_y (int): Початкова координата Y (1-8)
            to_x (int): Кінцева координата X (1-8)
            to_y (int): Кінцева координата Y (1-8)
            player (str): Гравець ('white' або 'black')
        
        Returns:
            bool: True, якщо хід допустимий, інакше False
        """
        board_term = self._board_python_to_prolog(board)
        query = f"valid_simple_move({board_term}, {from_x}, {from_y}, {to_x}, {to_y}, {player})"
        return bool(list(self.prolog.query(query)))
    
    def is_valid_king_move(self, board, from_x, from_y, to_x, to_y, player):
        board_term = self._board_python_to_prolog(board)
        query = f"valid_king_move({board_term}, {from_x}, {from_y}, {to_x}, {to_y}, {player})"
        return bool(list(self.prolog.query(query)))

    def is_valid_capture(self, board, from_x, from_y, to_x, to_y, player):
        """
        Перевіряє, чи є взяття допустимим
        
        Args:
            board (list): Поточна дошка
            from_x (int): Початкова координата X (1-8)
            from_y (int): Початкова координата Y (1-8)
            to_x (int): Кінцева координата X (1-8)
            to_y (int): Кінцева координата Y (1-8)
            player (str): Гравець ('white' або 'black')
        
        Returns:
            bool: True, якщо взяття допустиме, інакше False
        """
        board_term = self._board_python_to_prolog(board)
        query = f"valid_capture({board_term}, {from_x}, {from_y}, {to_x}, {to_y}, {player})"
        return bool(list(self.prolog.query(query)))
    
    def make_move(self, board, from_x, from_y, to_x, to_y, player):
        """
        Виконує хід
        
        Args:
            board (list): Поточна дошка
            from_x (int): Початкова координата X (1-8)
            from_y (int): Початкова координата Y (1-8)
            to_x (int): Кінцева координата X (1-8)
            to_y (int): Кінцева координата Y (1-8)
            player (str): Гравець ('white' або 'black')
        
        Returns:
            list: Нова дошка після ходу або None, якщо хід неможливий
        """
        board_term = self._board_python_to_prolog(board)
        piece = self.get_piece(board, from_x, from_y)

        # Спроба виконати взяття (для всіх типів фігур)
        capture_query = f"make_capture_move({board_term}, {from_x}, {from_y}, {to_x}, {to_y}, {player}, NewBoard)"
        capture_result = list(self.prolog.query(capture_query))
        
        if capture_result:
            return self._board_prolog_to_python(capture_result[0]["NewBoard"])

        # Якщо фігура - дамка, використовуємо окрему логіку
        if piece in ["wk", "bk"]:
            # Спроба зробити хід дамкою (можливі довгі ходи)
            king_query = f"make_king_move({board_term}, {from_x}, {from_y}, {to_x}, {to_y}, {player}, NewBoard)"
            king_result = list(self.prolog.query(king_query))
            if king_result:
                return self._board_prolog_to_python(king_result[0]["NewBoard"])
        else:
            # Звичайний хід для простих шашок
            move_query = f"make_simple_move({board_term}, {from_x}, {from_y}, {to_x}, {to_y}, {player}, NewBoard)"
            move_result = list(self.prolog.query(move_query))
            if move_result:
                return self._board_prolog_to_python(move_result[0]["NewBoard"])

        return None
    
    def print_board(self, board):
        """
        Виводить дошку в консоль
        
        Args:
            board (list): Дошка для виведення
        """
        print("  1 2 3 4 5 6 7 8")
        for i, row in enumerate(board):
            print(f"{i+1} ", end="")
            for cell in row:
                if cell == "empty":
                    print(". ", end="")
                elif cell == "w":
                    print("w ", end="")
                elif cell == "b":
                    print("b ", end="")
                elif cell == "wk":
                    print("W ", end="")
                elif cell == "bk":
                    print("B ", end="")
            print()

    def ai_make_move(self, board, difficulty):
        """Виконує хід через Prolog AI"""
        board_term = self._board_python_to_prolog(board)
        try:
            result = list(self.prolog.query(
                f"ai_make_move({board_term}, {difficulty}, NewBoard, (FromX, FromY, ToX, ToY))"
            ))[0]
            return (
                self._board_prolog_to_python(result["NewBoard"]),
                (result["FromX"], result["FromY"], result["ToX"], result["ToY"])
            )
        except Exception as e:
            print(f"AI error: {e}")
            return None, None


# Тестування інтерфейсу
def test_interface():
    """
    Функція для тестування інтерфейсу між Prolog і Python
    """
    try:
        # Створюємо інтерфейс
        interface = CheckersInterface()
        
        # Отримуємо початкову дошку
        board = interface.get_initial_board()
        print("Початкова дошка:")
        interface.print_board(board)
        
        # Тестуємо функцію get_piece
        piece = interface.get_piece(board, 1, 6)
        print(f"\nФігура на позиції (1,6): {piece}")
        
        # Тестуємо перевірку допустимого ходу
        is_valid = interface.is_valid_move(board, 1, 6, 2, 5, "white")
        print(f"\nЧи є хід (1,6) -> (2,5) допустимим: {is_valid}")
        
        # Тестуємо виконання ходу
        new_board = interface.make_move(board, 1, 6, 2, 5, "white")
        if new_board:
            print("\nДошка після ходу (1,6) -> (2,5):")
            interface.print_board(new_board)
        else:
            print("\nХід неможливий!")
        
        # Тестуємо порожню дошку
        empty_board = interface.get_empty_board()
        print("\nПорожня дошка:")
        interface.print_board(empty_board)
        
        return True
    except Exception as e:
        print(f"Помилка під час тестування: {e}")
        return False


if __name__ == "__main__":
    test_interface()
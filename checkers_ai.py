import random
from checkers_interface import CheckersInterface

class CheckersAI:
    """
    Штучний інтелект для гри в шашки
    """
    def __init__(self, difficulty="medium"):
        """
        Ініціалізація AI з вибраним рівнем складності
        
        Args:
            difficulty (str): Рівень складності AI ('easy', 'medium', 'hard')
        """
        self.interface = CheckersInterface()
        self.difficulty = difficulty
        self.player_color = "black"  # AI завжди грає за чорних
        
        # Визначення глибини пошуку залежно від складності
        self.depth_map = {
            "easy": 1,
            "medium": 3,
            "hard": 5
        }
    
    def make_move(self, board):
        """
        Вибирає та виконує хід залежно від складності
        
        Args:
            board (list): Поточний стан дошки
        
        Returns:
            tuple: Новий стан дошки та інформація про хід (from_x, from_y, to_x, to_y)
        """
        if self.difficulty == "easy":
            return self.make_random_move(board)
        else:
            return self.make_best_move(board)
    
    def make_random_move(self, board):
        """
        Вибирає випадковий допустимий хід
        
        Args:
            board (list): Поточний стан дошки
        
        Returns:
            tuple: Новий стан дошки та інформація про хід (from_x, from_y, to_x, to_y)
        """
        # Отримуємо всі можливі ходи
        all_moves = self.get_all_possible_moves(board, self.player_color)
        if not all_moves:
            return None, (None, None, None, None)
        
        # Віддаємо перевагу взяттям, якщо вони є
        captures = [move for move in all_moves if abs(move[2] - move[0]) == 2]
        
        if captures:
            # Вибираємо випадкове взяття
            move = random.choice(captures)
        else:
            # Вибираємо випадковий хід
            move = random.choice(all_moves)
        
        from_x, from_y, to_x, to_y = move
        new_board = self.interface.make_move(board, from_x, from_y, to_x, to_y, self.player_color)
        
        return new_board, move
    
    def make_best_move(self, board):
        """
        Вибирає найкращий хід за допомогою мінімакс алгоритму
        
        Args:
            board (list): Поточний стан дошки
        
        Returns:
            tuple: Новий стан дошки та інформація про хід (from_x, from_y, to_x, to_y)
        """
        depth = self.depth_map[self.difficulty]
        _, best_move = self.minimax(board, depth, float('-inf'), float('inf'), True)
        
        if best_move is None:
            return None, (None, None, None, None)
        
        from_x, from_y, to_x, to_y = best_move
        new_board = self.interface.make_move(board, from_x, from_y, to_x, to_y, self.player_color)
        
        return new_board, best_move
    
    def minimax(self, board, depth, alpha, beta, is_maximizing):
        """
        Алгоритм мінімакс з альфа-бета відсіканням
        
        Args:
            board (list): Поточний стан дошки
            depth (int): Глибина пошуку
            alpha (float): Альфа значення
            beta (float): Бета значення
            is_maximizing (bool): True, якщо це хід AI, False для людини
        
        Returns:
            tuple: Оцінка позиції та найкращий хід
        """
        # Базовий випадок: досягнуто максимальну глибину або гра закінчена
        if depth == 0 or self.is_game_over(board):
            return self.evaluate_board(board), None
        
        current_player = self.player_color if is_maximizing else "white"
        all_moves = self.get_all_possible_moves(board, current_player)
        
        if not all_moves:
            # Якщо немає можливих ходів, це програш для поточного гравця
            return float('-inf') if is_maximizing else float('inf'), None
        
        best_move = None
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in all_moves:
                from_x, from_y, to_x, to_y = move
                new_board = self.interface.make_move(board, from_x, from_y, to_x, to_y, current_player)
                
                # Перевіряємо на додаткові взяття
                additional_captures = False
                if abs(to_x - from_x) == 2:  # Було взяття
                    next_moves = self.get_possible_captures_from(new_board, to_x, to_y, current_player)
                    if next_moves:
                        additional_captures = True
                
                # Якщо є додаткові взяття, не змінюємо гравця
                if additional_captures:
                    eval_val, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                else:
                    eval_val, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                
                if eval_val > max_eval:
                    max_eval = eval_val
                    best_move = move
                
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in all_moves:
                from_x, from_y, to_x, to_y = move
                new_board = self.interface.make_move(board, from_x, from_y, to_x, to_y, current_player)
                
                # Перевіряємо на додаткові взяття
                additional_captures = False
                if abs(to_x - from_x) == 2:  # Було взяття
                    next_moves = self.get_possible_captures_from(new_board, to_x, to_y, current_player)
                    if next_moves:
                        additional_captures = True
                
                # Якщо є додаткові взяття, не змінюємо гравця
                if additional_captures:
                    eval_val, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                else:
                    eval_val, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                
                if eval_val < min_eval:
                    min_eval = eval_val
                    best_move = move
                
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
            
            return min_eval, best_move
    
    def get_all_possible_moves(self, board, player):
        """
        Отримує всі можливі ходи для гравця
        
        Args:
            board (list): Поточний стан дошки
            player (str): Гравець ('white' або 'black')
        
        Returns:
            list: Список ходів у вигляді (from_x, from_y, to_x, to_y)
        """
        all_moves = []
        captures_required = False
        
        # Спочатку перевіряємо, чи є можливі взяття
        for y in range(1, 9):
            for x in range(1, 9):
                piece = self.interface.get_piece(board, x, y)
                is_player_piece = False
                
                if player == "white" and (piece == "w" or piece == "wk"):
                    is_player_piece = True
                elif player == "black" and (piece == "b" or piece == "bk"):
                    is_player_piece = True
                
                if is_player_piece:
                    # Перевіряємо можливі взяття для цієї шашки
                    captures = self.get_possible_captures_from(board, x, y, player)
                    if captures:
                        if not captures_required:
                            # Якщо це перше знайдене взяття, очищаємо список ходів
                            all_moves = []
                            captures_required = True
                        all_moves.extend(captures)
        
        # Якщо немає взять, збираємо звичайні ходи
        if not captures_required:
            for y in range(1, 9):
                for x in range(1, 9):
                    piece = self.interface.get_piece(board, x, y)
                    is_player_piece = False
                    
                    if player == "white" and (piece == "w" or piece == "wk"):
                        is_player_piece = True
                    elif player == "black" and (piece == "b" or piece == "bk"):
                        is_player_piece = True
                    
                    if is_player_piece:
                        # Перевіряємо можливі ходи для цієї шашки
                        moves = self.get_possible_moves_from(board, x, y, player)
                        all_moves.extend(moves)
        
        return all_moves
    
    def get_possible_moves_from(self, board, x, y, player):
        """
        Отримує всі можливі ходи для шашки на позиції (x, y)
        
        Args:
            board (list): Поточний стан дошки
            x (int): Координата X (1-8)
            y (int): Координата Y (1-8)
            player (str): Гравець ('white' або 'black')
        
        Returns:
            list: Список ходів у вигляді (from_x, from_y, to_x, to_y)
        """
        moves = []
        piece = self.interface.get_piece(board, x, y)
        
        # Перевіряємо всі можливі напрямки руху
        directions = []
        if piece == "w" or piece == "wk":
            directions.extend([(-1, -1), (1, -1)])  # Вверх-вліво та вверх-вправо
        if piece == "b" or piece == "bk":
            directions.extend([(-1, 1), (1, 1)])  # Вниз-вліво та вниз-вправо
        if piece == "wk" or piece == "bk":
            # Королі можуть рухатись у всіх напрямках по діагоналі
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    # Перевіряємо всі можливі відстані
                    for dist in range(1, 8):
                        to_x = x + dx * dist
                        to_y = y + dy * dist
                        if 1 <= to_x <= 8 and 1 <= to_y <= 8:
                            if self.interface.is_valid_move(board, x, y, to_x, to_y, player):
                                moves.append((x, y, to_x, to_y))
                        else:
                            break  # Вийшли за межі дошки
        else:
            # Звичайні шашки рухаються лише на 1 клітинку
            for dx, dy in directions:
                to_x = x + dx
                to_y = y + dy
                if 1 <= to_x <= 8 and 1 <= to_y <= 8:
                    if self.interface.is_valid_move(board, x, y, to_x, to_y, player):
                        moves.append((x, y, to_x, to_y))
        
        return moves
    
    def get_possible_captures_from(self, board, x, y, player):
        """
        Отримує всі можливі взяття для шашки на позиції (x, y)
        
        Args:
            board (list): Поточний стан дошки
            x (int): Координата X (1-8)
            y (int): Координата Y (1-8)
            player (str): Гравець ('white' або 'black')
        
        Returns:
            list: Список взять у вигляді (from_x, from_y, to_x, to_y)
        """
        captures = []
        piece = self.interface.get_piece(board, x, y)
        
        # Перевіряємо всі можливі напрямки взяття
        directions = []
        if piece == "w" or piece == "wk" or piece == "b" or piece == "bk":
            # Всі шашки можуть брати в будь-якому напрямку
            directions = [(-2, -2), (2, -2), (-2, 2), (2, 2)]
        
        for dx, dy in directions:
            to_x = x + dx
            to_y = y + dy
            if 1 <= to_x <= 8 and 1 <= to_y <= 8:
                if self.interface.is_valid_capture(board, x, y, to_x, to_y, player):
                    captures.append((x, y, to_x, to_y))
        
        return captures
    
    def is_game_over(self, board):
        """
        Перевіряє, чи гра закінчена
        
        Args:
            board (list): Поточний стан дошки
        
        Returns:
            bool: True, якщо гра закінчена, інакше False
        """
        # Гра закінчена, якщо один з гравців не має шашок або ходів
        white_moves = self.get_all_possible_moves(board, "white")
        black_moves = self.get_all_possible_moves(board, "black")
        
        return not white_moves or not black_moves
    
    def evaluate_board(self, board):
        """
        Оцінює стан дошки з точки зору AI
        
        Args:
            board (list): Поточний стан дошки
        
        Returns:
            float: Оцінка позиції
        """
        white_score = 0
        black_score = 0
        
        # Підраховуємо кількість шашок кожного кольору та їх розташування
        for y in range(1, 9):
            for x in range(1, 9):
                piece = self.interface.get_piece(board, x, y)
                if piece == "w":
                    white_score += 100
                    # Бонус за просування вперед
                    white_score += (8 - y) * 5
                    # Бонус за центральні позиції
                    if 3 <= x <= 6 and 3 <= y <= 6:
                        white_score += 10
                elif piece == "wk":
                    white_score += 300  # Королі коштують більше
                elif piece == "b":
                    black_score += 100
                    # Бонус за просування вперед
                    black_score += y * 5
                    # Бонус за центральні позиції
                    if 3 <= x <= 6 and 3 <= y <= 6:
                        black_score += 10
                elif piece == "bk":
                    black_score += 300  # Королі коштують більше
        
        # Додатковий бонус за можливість взяття
        white_captures = self.count_possible_captures(board, "white")
        black_captures = self.count_possible_captures(board, "black")
        
        white_score += white_captures * 50
        black_score += black_captures * 50
        
        # Повертаємо різницю з точки зору AI (чорний гравець)
        return black_score - white_score
    
    def count_possible_captures(self, board, player):
        """
        Підраховує кількість можливих взять для гравця
        
        Args:
            board (list): Поточний стан дошки
            player (str): Гравець ('white' або 'black')
        
        Returns:
            int: Кількість можливих взять
        """
        captures = 0
        
        for y in range(1, 9):
            for x in range(1, 9):
                piece = self.interface.get_piece(board, x, y)
                is_player_piece = False
                
                if player == "white" and (piece == "w" or piece == "wk"):
                    is_player_piece = True
                elif player == "black" and (piece == "b" or piece == "bk"):
                    is_player_piece = True
                
                if is_player_piece:
                    captures_list = self.get_possible_captures_from(board, x, y, player)
                    captures += len(captures_list)
        
        return captures
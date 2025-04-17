% checkers.pl - Fixed checkers game logic with parameter indicators

% Board representation 8x8
% Using coordinates (X, Y), where X and Y are numbers from 1 to 8
% Game is played only on black squares

% Constants for piece representation
% empty - empty square
% w - white checker
% b - black checker
% wk - white king
% bk - black king

% initial_board(--Board)
% Initializes a standard starting position board
initial_board([
    [empty, b, empty, b, empty, b, empty, b],
    [b, empty, b, empty, b, empty, b, empty],
    [empty, b, empty, b, empty, b, empty, b],
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [w, empty, w, empty, w, empty, w, empty],
    [empty, w, empty, w, empty, w, empty, w],
    [w, empty, w, empty, w, empty, w, empty]
]).

% empty_board(--Board)
% Initializes a completely empty board for testing
empty_board([
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, empty, empty, empty, empty, empty, empty],
    [empty, empty, empty, empty, empty, empty, empty, empty]
]).

% get_piece(++Board, ++X, ++Y, --Piece)
% Get the piece at position (X, Y)
get_piece(Board, X, Y, Piece) :-
    X >= 1, X =< 8,
    Y >= 1, Y =< 8,
    nth1(Y, Board, Row),
    nth1(X, Row, Piece).

% is_empty(++Board, ++X, ++Y)
% Check if a square is empty
is_empty(Board, X, Y) :-
    get_piece(Board, X, Y, empty).

% is_player_piece(++Piece, --Player)
% Check if a piece belongs to a player
is_player_piece(w, white).
is_player_piece(wk, white).
is_player_piece(b, black).
is_player_piece(bk, black).

% opponent(++Player, --OpponentPlayer)
% Define opponent relationship
opponent(white, black).
opponent(black, white).

% valid_position(++X, ++Y)
% Check if position is within board boundaries
valid_position(X, Y) :-
    X >= 1, X =< 8,
    Y >= 1, Y =< 8.

% set_piece(++Board, ++X, ++Y, ++Piece, --NewBoard)
% Change board state: place a piece at a position
set_piece(Board, X, Y, Piece, NewBoard) :-
    valid_position(X, Y),
    set_piece_helper(Board, X, Y, Piece, 1, NewBoard).

% set_piece_helper(++BoardPart, ++X, ++Y, ++Piece, ++CurrentY, --NewBoardPart)
% Helper predicate to set a piece at specific position - processes rows
set_piece_helper([], _, _, _, _, []).
set_piece_helper([Row|Rest], X, Y, Piece, CurrentY, [NewRow|NewRest]) :-
    CurrentY =:= Y,
    set_row_piece(Row, X, Piece, 1, NewRow),
    NextY is CurrentY + 1,
    set_piece_helper(Rest, X, Y, Piece, NextY, NewRest).
set_piece_helper([Row|Rest], X, Y, Piece, CurrentY, [Row|NewRest]) :-
    CurrentY =\= Y,
    NextY is CurrentY + 1,
    set_piece_helper(Rest, X, Y, Piece, NextY, NewRest).

% set_row_piece(++RowPart, ++X, ++Piece, ++CurrentX, --NewRowPart)
% Helper predicate to set a piece at specific position - processes columns
set_row_piece([], _, _, _, []).
set_row_piece([_|Rest], X, Piece, CurrentX, [Piece|NewRest]) :-
    CurrentX =:= X,
    NextX is CurrentX + 1,
    set_row_piece(Rest, X, Piece, NextX, NewRest).
set_row_piece([Cell|Rest], X, Piece, CurrentX, [Cell|NewRest]) :-
    CurrentX =\= X,
    NextX is CurrentX + 1,
    set_row_piece(Rest, X, Piece, NextX, NewRest).

% valid_direction(++Player, ++FromY, ++ToY)
% Check direction of movement (white moves up, black moves down)
valid_direction(white, FromY, ToY) :- ToY < FromY.
valid_direction(black, FromY, ToY) :- ToY > FromY.

% valid_simple_move(++Board, ++FromX, ++FromY, ++ToX, ++ToY, ++Player)
% Basic rules for single move of a regular checker
valid_simple_move(Board, FromX, FromY, ToX, ToY, Player) :-
    get_piece(Board, FromX, FromY, Piece),
    is_player_piece(Piece, Player),
    is_empty(Board, ToX, ToY),
    valid_direction(Player, FromY, ToY),
    abs(ToX - FromX) =:= 1,
    abs(ToY - FromY) =:= 1.

% make_simple_move(++Board, ++FromX, ++FromY, ++ToX, ++ToY, ++Player, --NewBoard)
% Perform a simple move (non-capture)
make_simple_move(Board, FromX, FromY, ToX, ToY, Player, NewBoard) :-
    valid_simple_move(Board, FromX, FromY, ToX, ToY, Player),
    % Get the piece to move
    get_piece(Board, FromX, FromY, Piece),
    % Remove the piece from original position
    set_piece(Board, FromX, FromY, empty, TempBoard),
    % Check for promotion to king
    (should_promote(Piece, ToY, PromotedPiece) ->
        set_piece(TempBoard, ToX, ToY, PromotedPiece, NewBoard)
    ;
        set_piece(TempBoard, ToX, ToY, Piece, NewBoard)
    ).

% should_promote(++Piece, ++Y, --PromotedPiece)
% Promotion to king
should_promote(w, 1, wk) :- !.  % White piece reaches top row
should_promote(b, 8, bk) :- !.  % Black piece reaches bottom row
should_promote(Piece, _, Piece).  % No promotion

% valid_capture(++Board, ++FromX, ++FromY, ++ToX, ++ToY, ++Player)
% Capture move logic
valid_capture(Board, FromX, FromY, ToX, ToY, Player) :-
    get_piece(Board, FromX, FromY, Piece),
    is_player_piece(Piece, Player),
    is_empty(Board, ToX, ToY),
    % Calculate middle position (captured piece position)
    MidX is (FromX + ToX) // 2,
    MidY is (FromY + ToY) // 2,
    % Check if valid diagonal
    abs(ToX - FromX) =:= 2,
    abs(ToY - FromY) =:= 2,
    % Check if there's an opponent's piece to capture
    get_piece(Board, MidX, MidY, CapturedPiece),
    is_player_piece(CapturedPiece, OpponentPlayer),
    opponent(Player, OpponentPlayer).

% make_capture_move(++Board, ++FromX, ++FromY, ++ToX, ++ToY, ++Player, --NewBoard)
% Perform a capture move
make_capture_move(Board, FromX, FromY, ToX, ToY, Player, NewBoard) :-
    valid_capture(Board, FromX, FromY, ToX, ToY, Player),
    % Get the piece to move
    get_piece(Board, FromX, FromY, Piece),
    % Calculate middle position (captured piece position)
    MidX is (FromX + ToX) // 2,
    MidY is (FromY + ToY) // 2,
    % Remove the piece from original position
    set_piece(Board, FromX, FromY, empty, TempBoard1),
    % Remove the captured piece
    set_piece(TempBoard1, MidX, MidY, empty, TempBoard2),
    % Check for promotion to king
    (should_promote(Piece, ToY, PromotedPiece) ->
        set_piece(TempBoard2, ToX, ToY, PromotedPiece, NewBoard)
    ;
        set_piece(TempBoard2, ToX, ToY, Piece, NewBoard)
    ).

% sign(+N, --Sign)
% Helper function - sign of a number
sign(N, 1) :- N > 0, !.
sign(N, -1) :- N < 0, !.
sign(0, 0).

% valid_king_move(++Board, ++FromX, ++FromY, ++ToX, ++ToY, ++Player)
% King movement rules - checking diagonal path
valid_king_move(Board, FromX, FromY, ToX, ToY, Player) :-
    get_piece(Board, FromX, FromY, Piece),
    (Piece == wk ; Piece == bk),  % Must be a king
    is_player_piece(Piece, Player),
    is_empty(Board, ToX, ToY),
    % Kings move diagonally any distance
    DX is abs(ToX - FromX),
    DY is abs(ToY - FromY),
    DX =:= DY,
    DX > 0,
    % Path must be clear
    path_is_clear(Board, FromX, FromY, ToX, ToY).

% path_is_clear(++Board, ++FromX, ++FromY, ++ToX, ++ToY)
% Check if path is clear for king movement
path_is_clear(Board, FromX, FromY, ToX, ToY) :-
    % Calculate step direction
    DirX is sign(ToX - FromX),
    DirY is sign(ToY - FromY),
    % Start from position after FromX, FromY
    NextX is FromX + DirX,
    NextY is FromY + DirY,
    path_is_clear_helper(Board, NextX, NextY, ToX, ToY, DirX, DirY).

% path_is_clear_helper(++Board, ++X, ++Y, ++ToX, ++ToY, ++DirX, ++DirY)
% Recursively check if all squares in path are empty
path_is_clear_helper(_, X, Y, X, Y, _, _) :- !.  % Reached destination
path_is_clear_helper(Board, X, Y, ToX, ToY, DirX, DirY) :-
    X \= ToX, Y \= ToY,  % Not at destination yet
    is_empty(Board, X, Y),  % Current position must be empty
    NextX is X + DirX,
    NextY is Y + DirY,
    path_is_clear_helper(Board, NextX, NextY, ToX, ToY, DirX, DirY).

% print_board(++Board)
% Display board (for testing)
print_board(Board) :-
    writeln('  1 2 3 4 5 6 7 8'),
    print_board_rows(Board, 1).

% print_board_rows(++Rows, ++RowNum)
% Helper for printing board rows
print_board_rows([], _).
print_board_rows([Row|Rest], RowNum) :-
    write(RowNum), write(' '),
    print_row(Row),
    writeln(''),
    NextRowNum is RowNum + 1,
    print_board_rows(Rest, NextRowNum).

% print_row(++Row)
% Helper for printing a single row
print_row([]).
print_row([empty|Rest]) :- write('. '), print_row(Rest).
print_row([w|Rest]) :- write('w '), print_row(Rest).
print_row([b|Rest]) :- write('b '), print_row(Rest).
print_row([wk|Rest]) :- write('W '), print_row(Rest).
print_row([bk|Rest]) :- write('B '), print_row(Rest).

% test_get_piece
% Test basic functionality
test_get_piece :-
    initial_board(Board),
    get_piece(Board, 2, 1, Piece),
    writeln('Piece at position (2,1):'),
    writeln(Piece),
    get_piece(Board, 1, 6, Piece2),
    writeln('Piece at position (1,6):'),
    writeln(Piece2).

% test_valid_move
% Test move validity
test_valid_move :-
    initial_board(Board),
    writeln('Checking move (1,6) -> (2,5):'),
    (valid_simple_move(Board, 1, 6, 2, 5, white) -> 
        writeln('Move allowed') ; 
        writeln('Move not possible')
    ),
    writeln('Checking move (2,3) -> (3,4):'),
    (valid_simple_move(Board, 2, 3, 3, 4, black) -> 
        writeln('Move allowed') ; 
        writeln('Move not possible')
    ).

% test_set_piece
% Test board modification
test_set_piece :-
    initial_board(Board),
    writeln('Initial board:'),
    print_board(Board),
    set_piece(Board, 1, 4, w, NewBoard),
    writeln('Board after moving white piece to position (1,4):'),
    print_board(NewBoard).

% run_basic_tests
% Run basic test cases
run_basic_tests :-
    writeln('=== Testing piece retrieval ==='),
    test_get_piece,
    writeln(''),
    writeln('=== Testing move rules ==='),
    test_valid_move,
    writeln(''),
    writeln('=== Testing board modification ==='),
    test_set_piece.

% test_promotion
% Fixed test_promotion function
test_promotion :-
    % Setup board with white piece at row 2
    empty_board(EmptyBoard),
    set_piece(EmptyBoard, 1, 2, w, Board1),
    writeln('Board with white piece at (1,2):'),
    print_board(Board1),
    
    % Move to row 1 (should promote)
    make_simple_move(Board1, 1, 2, 2, 1, white, NewBoard),
    writeln('After move to (2,1) - should be promoted to king:'),
    print_board(NewBoard),
    get_piece(NewBoard, 2, 1, ResultPiece),
    write('Resulting piece: '), writeln(ResultPiece).

% test_capture
% Test capture logic
test_capture :-
    % Create a board with capture opportunity
    empty_board(EmptyBoard),
    set_piece(EmptyBoard, 3, 5, w, Board1),  % White piece
    set_piece(Board1, 4, 4, b, Board2),      % Black piece to capture
    writeln('Board with capture opportunity:'),
    print_board(Board2),
    
    % Test if capture is valid
    writeln('Checking if capture (3,5) -> (5,3) is valid:'),
    (valid_capture(Board2, 3, 5, 5, 3, white) -> 
        writeln('Capture is valid') ; 
        writeln('Capture is not valid')
    ),
    
    % Execute capture
    make_capture_move(Board2, 3, 5, 5, 3, white, NewBoard),
    writeln('After capture:'),
    print_board(NewBoard).

% test_king_movement
% Test king movement
test_king_movement :-
    % Create a board with kings
    empty_board(EmptyBoard),
    set_piece(EmptyBoard, 4, 4, wk, KingBoard),
    writeln('Board with white king at (4,4):'),
    print_board(KingBoard),
    
    % Test diagonal movements
    writeln('Testing king movement from (4,4) to (7,7):'),
    (valid_king_move(KingBoard, 4, 4, 7, 7, white) -> 
        writeln('Move is valid') ; 
        writeln('Move is not valid')
    ),
    
    writeln('Testing king movement from (4,4) to (1,1):'),
    (valid_king_move(KingBoard, 4, 4, 1, 1, white) -> 
        writeln('Move is valid') ; 
        writeln('Move is not valid')
    ),
    
    % Test blocked path
    set_piece(KingBoard, 5, 5, b, BlockedBoard),
    writeln('Board with obstacle at (5,5):'),
    print_board(BlockedBoard),
    
    writeln('Testing king movement with obstacle:'),
    (valid_king_move(BlockedBoard, 4, 4, 7, 7, white) -> 
        writeln('Move is valid (wrong!)') ; 
        writeln('Move is not valid (correct!)')
    ).

% run_extended_tests
% Run tests in separate parts
run_extended_tests :-
    writeln('=== Testing basic promotion logic ==='),
    test_promotion,
    writeln(''),
    writeln('=== Testing basic capture logic ==='),
    test_capture,
    writeln(''),
    writeln('=== Testing king movement ==='),
    test_king_movement.

% Entry point
:- initialization(run_basic_tests).
:- initialization(run_extended_tests).
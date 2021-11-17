from sys import path
path.append('./')

from typing import NoReturn, Tuple, List, Optional
from enum import Enum, auto

from constants import HEIGHT, WIDTH


class PlayerType(Enum):
    """プレイヤータイプ

    Attributes:
        FIRST: 黒
        SECOND: 白
    """

    FIRST = auto()
    SECOND = auto()


class SquareType(Enum):
    """マスタイプ

    Attributes:
        FIRST: 黒
        SECOND: 白
        VACANT: 空
    """

    FIRST = auto()
    SECOND = auto()
    VACANT = auto()


def to_square_type(player: PlayerType = None) -> SquareType:
    """PlayerType -> SquareType"""

    if player is PlayerType.FIRST:
        return SquareType.FIRST
    if player is PlayerType.SECOND:
        return SquareType.SECOND
    return SquareType.VACANT


class Move:
    """置き位置

    Args:
        player(PlayerType): 置いた人
        x(int): 行
        y(int): 列
    """

    def __init__(self, x: int, y: int, *,
                 player: PlayerType = None,
                 ):
        self._player = player
        self._x = x
        self._y = y

    def __repr__(self):
        if self.player is not None:
            return f'{self.player}{self.point}'
        return f'Move{self.point}'

    @property
    def player(self) -> PlayerType:
        """コマの持ち主"""

        return self._player

    @player.setter
    def player(self, player: PlayerType) -> NoReturn:
        self._player = player

    @property
    def point(self) -> Tuple[int, int]:
        return (self._x, self._y)

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int) -> NoReturn:
        if value < 0 or self.HEIGHT <= value:
            raise ValueError
        self._x = value

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int) -> NoReturn:
        if value < 0 or self.WIDTH <= value:
            raise ValueError
        self._y = value


# 黒は最初中央に置くs
FIRST_MOVE = Move(7, 7)
NONE_MOVE = Move(None, None)


class Board:
    """盤面の情報

    Args:
        turn(PlayerType): 現在のターン（手を置く人）
        board(List[List[SquareType]]): 盤面
    """

    _score_sheet = []
    _putter = PlayerType.FIRST

    def __init__(self):
        self._board = [
            [SquareType.VACANT for i in range(HEIGHT)] for i in range(WIDTH)]

    @property
    def score_sheet(self) -> List[Move]:
        """スコアシート"""

        return self._score_sheet

    @property
    def board(self) -> List[List[SquareType]]:
        """盤面"""

        return self._board

    @property
    def turn(self) -> PlayerType:
        """現在のターン数。何も置いていない時 0"""

        return len(self._score_sheet)

    @property
    def putter(self) -> PlayerType:
        """次に置くプレイヤー"""

        return self._putter

    def add_move(self, move: Move) -> NoReturn:
        """石を置く"""

        if move.player is None:
            move.player = self.putter

        x, y = move.point
        self.board[x][y] = to_square_type(move.player)
        self.score_sheet.append(move)
        self.increment_turn()

    def pass_turn(self) -> NoReturn:
        """有効手がない場合にターンを飛ばす。"""

        self.score_sheet.append(NONE_MOVE)
        self.increment_turn()

    def increment_turn(self) -> NoReturn:
        """次ターンへ遷移"""

        if self.putter == PlayerType.FIRST:
            self._putter = PlayerType.SECOND
        else:
            self._putter = PlayerType.FIRST


class Renju(Board):
    _finished = False
    _winner = None

    def __init__(self):
        super().__init__()

    def add_move(self, move: Move) -> NoReturn:
        if move.player is None:
            move.player = self.putter

        if self.finished:
            raise ValueError(f"game is already finished")

        if not self.is_legal_move(move):
            raise ValueError(f"can't move to {move.point}")

        super().add_move(move)

        if self.check_finished():
            self._finished = True
            self._winner = move.player

    def is_legal_move(self, move: Move) -> bool:
        """その位置に置くことができるとき True

        Todo: 黒の禁手処理の実装
        """

        (x, y), player = move.point, move.player

        # 初手は中央のみ
        if self.turn == 0 and move is not FIRST_MOVE:
            return False

        # すでに置かれている
        if self.board[x][y] is not SquareType.VACANT:
            return False

        # 白は禁手がない
        if player is PlayerType.SECOND:
            return True

        # 黒の禁手処理

        return True

    def check_finished(self) -> bool:
        """ゲームが終了条件を満たしているとき True"""

        # 横方向
        for x in range(HEIGHT):
            count = 0 if self.board[x][0] is SquareType.VACANT else 1
            for y in range(1, WIDTH):
                if self.board[x][y] is SquareType.VACANT:
                    count = 0
                    continue

                if self.board[x][y] == self.board[x][y - 1]:
                    count += 1
                else:
                    count = 1

                if count >= 5:
                    return True

        # 縦方向
        for y in range(WIDTH):
            count = 0 if self.board[0][y] is SquareType.VACANT else 1
            for x in range(1, HEIGHT):
                if self.board[x][y] is SquareType.VACANT:
                    count = 0
                    continue

                if self.board[x][y] == self.board[x - 1][y]:
                    count += 1
                else:
                    count = 1

                if count >= 5:
                    return True

        # 左下斜方向
        for xi in range(HEIGHT):
            count = 0 if self.board[xi][0] is SquareType.VACANT else 1
            for yi in range(1, WIDTH - xi):
                x, y = xi + yi, yi

                if self.board[x][y] is SquareType.VACANT:
                    count = 0
                    continue

                if self.board[x][y] == self.board[x - 1][y - 1]:
                    count += 1
                else:
                    count = 1

                if count >= 5:
                    return True

        # 右上斜方向
        for yi in range(1, WIDTH):
            count = 0 if self.board[0][yi] is SquareType.VACANT else 1
            for xi in range(1, HEIGHT - yi):
                x, y = xi, yi + xi

                if self.board[x][y] is SquareType.VACANT:
                    count = 0
                    continue

                if self.board[x][y] == self.board[x - 1][y - 1]:
                    count += 1
                else:
                    count = 1

                if count >= 5:
                    return True

        return False

    @property
    def finished(self) -> bool:
        """ゲームが終了しているとき True"""

        return self._finished

    @property
    def winner(self) -> Optional[PlayerType]:
        """勝者がいる場合は勝者を、いないとき None を返す。"""

        return self._winner

    def print_ascii(self) -> NoReturn:
        for row in self.board:
            for col in row:
                if col == SquareType.FIRST:
                    print('o', end='')
                if col == SquareType.SECOND:
                    print('x', end='')
                if col == SquareType.VACANT:
                    print('.', end='')
            print('')

        if self.finished:
            print(f'GAME IS FINISHED: WINNER = {self.winner}')


if __name__ == '__main__':
    renju = Renju()

    renju.add_move(FIRST_MOVE)  # Move(7, 7)
    renju.add_move(Move(0, 0))
    renju.add_move(Move(1, 0))
    renju.add_move(Move(0, 1))
    renju.add_move(Move(1, 1))
    renju.add_move(Move(0, 2))
    renju.add_move(Move(1, 2))
    renju.add_move(Move(0, 3))
    renju.add_move(Move(1, 3))
    renju.add_move(Move(0, 4))
#    renju.add_move(Move(1, 4))

    renju.print_ascii()

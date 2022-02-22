import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.__str__())


from typing import NoReturn, Tuple, List, Optional
from enum import Enum, auto

from constants import HEIGHT, WIDTH


class IllegalMove(Exception):
    """禁手"""

    pass


class PlayerType(Enum):
    """プレイヤータイプ

    Attributes:
        FIRST: 黒
        SECOND: 白
    """

    FIRST = auto()
    SECOND = auto()


def get_opposite(player: PlayerType) -> PlayerType:
    if player is PlayerType.FIRST:
        return PlayerType.SECOND
    return PlayerType.FIRST


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

    def __eq__(self, other) -> bool:
        if not isinstance(other, Move):
            return NotImplemented

        return self.player == other.player and\
            self.x == other.x and \
            self.y == other.y

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


# 黒は最初中央に置く
FIRST_MOVE = Move(7, 7, player=PlayerType.FIRST)
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

    @property
    def height(self) -> int:
        return HEIGHT

    @property
    def width(self) -> int:
        return WIDTH

    def add_move(self, move: Move) -> NoReturn:
        """石を置く"""
        if not isinstance(move, Move):
            move = Move(*move)

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

    def decrement_turn(self) -> NoReturn:
        """前ターンへ遷移"""

        self.increment_turn()


class Renju(Board):
    _finished = False
    _winner = None

    def __init__(self):
        super().__init__()

    def pop(self) -> NoReturn:
        """一手戻す"""

        if self.turn == 0:
            raise Exception

        move = self._score_sheet[-1]

        x, y = move.point
        self.board[x][y] = SquareType.VACANT
        self._score_sheet.pop()
        self.decrement_turn()

        self._finished, self._winner = False, None

    def add_move(self, move: Move) -> NoReturn:
        if not isinstance(move, Move):
            move = Move(*move)

        if move.player is None:
            move.player = self.putter

        if self.finished:
            raise ValueError(f"game is already finished")

        # 禁手を置いたときは、置いた方の負け
        if not self.is_legal_move(move):
            self._finished = True
            self._winner = get_opposite(self.putter)
            raise IllegalMove

        super().add_move(move)

        # 勝利判定
        res = self.renzoku(move)
        if max(res) >= 5:
            self._finished = True
            self._winner = move.player

    def is_legal_move(self, move: Move) -> bool:
        """その位置に置くことができるとき True

        Todo: 黒の禁手処理の実装
        """

        if not isinstance(move, Move):
            move = Move(*move)

        if move.player is None:
            move.player = self.putter

        (x, y), player = move.point, move.player

        if player is None:
            player = self.putter

        # 初手は中央のみ
        if self.turn == 0 and move != FIRST_MOVE:
            return False

        # すでに置かれている
        if self.board[x][y] is not SquareType.VACANT:
            return False

        # 白は禁手がない
        if player is PlayerType.SECOND:
            return True

        # 黒の禁手処理
        res = self.renzoku(move)
        if res.count(3) > 1:  # 三三
            return False
        if res.count(4) > 1:  # 四四
            return False
        if max(res) > 5:  # 長連
            return False

        return True

    def renzoku(self, move: Move) -> bool:
        """move に置いたときにできる連続を見つける"""

        res = []
        directions = [(0, 1), (-1, 1), (-1, 0), (-1, -1)]
        for (dx, dy) in directions:
            my_type = to_square_type(move.player)
            count = 1

            x, y = move.x, move.y
            while True:
                x += dx
                y += dy

                # 盤外
                if x < 0 or y < 0 or x >= HEIGHT or y >= WIDTH:
                    break

                if self.board[x][y] is my_type:
                    count += 1
                else:
                    break

            x, y = move.x, move.y
            while True:
                x -= dx
                y -= dy

                # 盤外
                if x < 0 or y < 0 or x >= HEIGHT or y >= WIDTH:
                    break

                if self.board[x][y] is my_type:
                    count += 1
                else:
                    break

            res.append(count)

        return res

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
    pass

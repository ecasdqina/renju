import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.__str__())


from prompt_toolkit.application import Application
from prompt_toolkit.filters import IsDone
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.layout.containers import ScrollOffsets
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.layout import Layout

import asyncio
from typing import Dict, Tuple, NoReturn, Optional

from game import SquareType, Renju


class BoardControl(FormattedTextControl):
    class Square:
        """マスの情報を持つ

        Attributes:
            square(Square): マスの状態
            canput(bool): 後手がマスに置けるとき true
        """

        def __init__(self, *,
                     square: Optional[SquareType] = None,
                     canput: bool = None):
            self._square = square
            self._canput = canput

        @property
        def square(self) -> SquareType:
            return self._square

        @square.setter
        def square(self, square: SquareType) -> NoReturn:
            self._square = square

        @property
        def canput(self) -> bool:
            return self._canput

        @canput.setter
        def canput(self, canput: bool) -> NoReturn:
            self._canput = canput

        def convert_to_formatted_text(self, *,
                                      selected: bool = False,
                                      color_style: Dict[str, str],
                                      text_style: Dict[str, str],
                                      ) -> Tuple[str, str]:
            """マスの formatted_text を作成する"""

            assert self.square is not None

            color = color_style['selected'] if selected else None

            if self.square == SquareType.FIRST:
                if color is None:
                    color = color_style['first']
                return (color, text_style['first'])

            if self.square == SquareType.SECOND:
                if color is None:
                    color = color_style['second']
                return (color, text_style['second'])

            if self.canput or self.canput is None:
                if color is None:
                    color = color_style['canput']
                return (color, text_style['vacant'])
            else:
                if color is None:
                    color = color_style['cannotput']
                return (color, text_style['vacant'])

        def __repr__(self):
            return f'{self.square}'

    color_style = ({
        'first': '#FFFFFF',
        'second': '#FFFFFF',
        'canput': '#FFFF00',
        'cannotput': '#0000FF',
        'selected': '#FF0000',
    })
    text_style = ({
        'first': 'o',
        'second': 'x',
        'vacant': '.',
    })
    selected_index_x, selected_index_y = 0, 0

    def __init__(self, *,
                 renju: Renju,
                 prompt: bool = True,
                 color_style: Optional[Dict[str, str]] = None,
                 text_style: Optional[Dict[str, str]] = None,
                 **kwargs):
        self.renju = renju
        self._board = [[None for i in range(15)] for i in range(15)]

        for x in range(renju.height):
            for y in range(renju.width):
                square = renju.board[x][y]
                canput = renju.is_legal_move((x, y))
                self.board[x][y] = self.Square(square=square,
                                               canput=canput)

        self.prompt = prompt
        if not prompt:
            self.selected_index_x, self.selected_index_y = -1, -1

        if color_style is not None:
            self.color_style.update(color_style)

        if text_style is not None:
            self.text_style.update(text_style)

        super(BoardControl, self).__init__(
            self.make_formatted_text, **kwargs)

    @property
    def board(self):
        return self._board

    @property
    def height(self):
        return len(self._board)

    @property
    def width(self):
        return 0 if self.height == 0 else len(self._board[0])

    def make_formatted_text(self):
        formatted_text = []

        # ゲーム情報
        formatted_text.append(('#00ffff',
                               f'[Info] TURN = {self.renju.turn}\n'))
        formatted_text.append(('#00ffff',
                               f'[Info] Putter = {self.renju.putter}\n'))

        if self.renju.finished:
            formatted_text.append(('#00ff00',
                                   f'[Info] FINISHED! WINNER is {self.renju.winner}\n'))
        else:
            formatted_text.append(('#00ffff',
                                   f'[Select] {self.get_selected_index()}\n'))

        def append(square: self.Square, selected: bool = False):
            formatted_text.append(square.convert_to_formatted_text(
                color_style=self.color_style, text_style=self.text_style,
                selected=selected))

        for x in range(self.height):
            for y in range(self.width):
                selected = (x == self.selected_index_x and
                            y == self.selected_index_y)
                append(self.board[x][y], selected)
            formatted_text.append(('', '\n'))

        return formatted_text

    def get_selected_index(self) -> Tuple[int, int]:
        return (self.selected_index_x, self.selected_index_y)

    def check_puttable(self) -> bool:
        x, y = self.get_selected_index()

        return self.board[x][y].canput


def prompt(renju: Renju) -> Tuple[int, int]:
    """盤面のビジュアライズ・プロンプト

    人間に手を選ばせる。

    Args:


    Returns:
        Tuple[int, int]: 選択された位置
    """

    bc = BoardControl(renju=renju)

    HSContainer = HSplit([
        ConditionalContainer(
            Window(
                bc,
                width=D.exact(43),
                height=D(min=3),
                scroll_offsets=ScrollOffsets(top=1, bottom=1)
            ),
            filter=~IsDone())])
    layout = Layout(HSContainer)

    kb = KeyBindings()

    @kb.add('c-q', eager=True)
    @kb.add('c-c', eager=True)
    def _(event):
        event.app.exit(None)

    @kb.add('down', eager=True)
    def move_cursor_down(event):
        selected_index_x = bc.selected_index_x
        if selected_index_x + 1 < bc.height:
            bc.selected_index_x += 1

    @kb.add('up', eager=True)
    def move_cursor_up(event):
        selected_index_x = bc.selected_index_x
        if selected_index_x - 1 >= 0:
            bc.selected_index_x -= 1

    @kb.add('right', eager=True)
    def move_cursor_right(event):
        selected_index_y = bc.selected_index_y
        if selected_index_y + 1 < bc.width:
            bc.selected_index_y += 1

    @kb.add('left', eager=True)
    def move_cursor_left(event):
        selected_index_y = bc.selected_index_y
        if selected_index_y - 1 >= 0:
            bc.selected_index_y -= 1

    @kb.add('enter', eager=True)
    def set_answer(event):
        if not bc.check_puttable():
            return
        event.app.exit(None)

    app = Application(
        layout=layout,
        key_bindings=kb,
        mouse_support=False,
    )
    app.run()

    return bc.get_selected_index()


async def visualize_async(app, wait_militime: int = 500):
    try:
        await asyncio.wait_for(app.run_async(), wait_militime / 1000)
    except:
        pass


def visualize(*,
              renju: Renju,
              enter_to_next: bool = False,
              wait_militime: int = 500) -> NoReturn:
    """盤面のビジュアライズ

    ソルバの結果の表示のみ。

    Args:
        wait_time (Optional[int], optional): [description]. Defaults to None.
    """

    bc = BoardControl(renju=renju, prompt=False)

    HSContainer = HSplit([
        ConditionalContainer(
            Window(
                bc,
                width=D.exact(43),
                height=D(min=3),
                scroll_offsets=ScrollOffsets(top=1, bottom=1)
            ),
            filter=~IsDone())])
    layout = Layout(HSContainer)

    kb = KeyBindings()

    @kb.add('c-q', eager=True)
    @kb.add('c-c', eager=True)
    def _(event):
        event.app.exit(None)

    @kb.add('enter', eager=True)
    def _(event):
        event.app.exit(None)

    app = Application(
        layout=layout,
        key_bindings=kb,
        mouse_support=False,
        refresh_interval=0.5,
    )

    # Enter で次
    if enter_to_next:
        app.run()
        return

    asyncio.get_event_loop().run_until_complete(visualize_async(app, wait_militime))


if __name__ == '__main__':
    pass

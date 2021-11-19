import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.__str__())


import csv
from typing import NoReturn

from game import Renju, PlayerType


def read_csv(file: str) -> Renju:
    with open(file, newline='') as csvfile:
        score_sheet = csv.reader(csvfile,
                                 delimiter=',',
                                 quotechar='"').__next__()[1:]

        renju = Renju()
        for row in score_sheet:
            program, x, y = map(int, row.split(':'))

            renju.add_move((x, y))
        return renju


def dump_csv(file: str, renju: Renju) -> NoReturn:
    with open(file, 'w', newline='') as csvfile:
        text = []

        # 行数
        text.append(str(renju.turn))

        # 手
        for i in range(renju.turn):
            move = renju.score_sheet[i]
            x, y = move.point

            program = '1' if move.player == PlayerType.FIRST else '2'
            text.append(':'.join([program, str(x), str(y)]))

        csvfile.write(','.join(text) + '\n')


if __name__ == '__main__':
    pass

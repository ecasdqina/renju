import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.__str__())

import subprocess
from argparse import ArgumentParser
from typing import NoReturn
from pathlib import Path
from logging import getLogger, basicConfig, DEBUG

from game import IllegalMove, Renju, Move
from prompt import prompt, visualize
from sheet import dump_csv

logger = getLogger(__name__)


def run(*, renju: Renju, command: str, score_sheet: Path) -> NoReturn:
    try:
        process = subprocess.run(command.split() + [str(score_sheet)],
                                 capture_output=True)
        move = Move(*map(int, process.stdout.split()))
        visualize(renju=renju)
        renju.add_move(move)
    except IllegalMove:
        return
    except:
        raise


def human_run(renju: Renju) -> NoReturn:
    try:
        move = prompt(renju)
        renju.add_move(move)
    except IllegalMove:
        return
    except:
        raise


def main() -> NoReturn:
    parser = ArgumentParser()
    parser.add_argument('-f', '--first', default=None)
    parser.add_argument('-s', '--second', default=None)
    parser.add_argument('-o', '--out', default='./score_sheet.txt')
    args = parser.parse_args()

#    basicConfig(level=DEBUG)

    # スコアシート
    score_sheet = Path(args.out)
    score_sheet.unlink(missing_ok=True)
    score_sheet.touch(exist_ok=True)

    with open(score_sheet, 'w', newline='') as f:
        f.write('0')

    renju = Renju()

    def check_finished() -> NoReturn:
        if not renju.finished:
            return
        else:
            visualize(renju=renju, enter_to_next=True)
            sys.exit(0)

    while True:
        # 先手（黒）
        if args.first is None:
            human_run(renju=renju)
        else:
            run(renju=renju, command=args.first, score_sheet=score_sheet)

        dump_csv(score_sheet, renju)
        check_finished()

        # 後手（白）
        if args.second is None:
            human_run(renju=renju)
        else:
            pass

        dump_csv(score_sheet, renju)
        check_finished()


if __name__ == '__main__':
    main()

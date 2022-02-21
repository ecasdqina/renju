
from argparse import ArgumentParser
from random import shuffle

from renju.sheet import read_csv


def main():
    parser = ArgumentParser()
    parser.add_argument('score_sheet')
    args = parser.parse_args()

    renju = read_csv(args.score_sheet)

    win_moves, next_moves = [], []
    for x in range(renju.height):
        for y in range(renju.width):
            if not renju.is_legal_move((x, y)):
                continue
            next_moves.append((x, y))

            renju.add_move((x, y))
            if renju.finished:
                win_moves.append((x, y))
            renju.pop()

    if len(win_moves) != 0:
        print(*win_moves[0])
    else:
        shuffle(next_moves)
        print(*next_moves[0])


if __name__ == '__main__':
    main()

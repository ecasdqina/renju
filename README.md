# Renju

## game.py

連珠の実装

## prompt.py

ターミナル表示

## sheet.py

CSV 処理用

## main.py

ジャッジコード

## 使い方

requirements.txt を元に pip3 で依存ライブラリをインストール

### 対戦

実行方法をオプションで渡す、渡さなければ手で打つ。

```bash
$ python3/main.py -f 'python3 solver/random_solver.py' -s 'python3 solver/random_solver.py'
```

### ソルバー単体

引数に手順の CSV ファイルを指定して `solver/random_solver.py` を実行すると手を探索し標準出力に出力する。

```bash
$ python3 solver/random_solver.py score_sheet.txt
```

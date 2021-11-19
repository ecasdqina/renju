# Renju

## game.py

連珠の実装が入っています。

## prompt.py

ターミナルに表示するための補助用コード類が入っています。

## sheet.py

CSV 処理用のコードが入っています。

## main.py

ジャッジコードが入っています。

## 使い方

### インストール

pip3 で入ります。

### 対戦

実行方法をオプションで渡せば動きます。渡さなければ手で打つことになります。

```bash
$ renju -f 'python3 solver/random_solver.py' -s 'python3 solver/random_solver.py'
```

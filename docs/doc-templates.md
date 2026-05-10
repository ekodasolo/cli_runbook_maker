# Jinja2 テンプレートの解説と保守ガイド

## 概要

`templates/runbook.md.j2` は唯一のテンプレートファイル。CREATE / MODIFY / DELETE すべての操作タイプに対応する汎用テンプレートとして設計されている。新しいサービスやリソースを追加するときも、このテンプレートは変更しない（スニペットの追加で対応する）。

## Jinja2 環境の設定

テンプレートの動作を理解するには、`generate.py` で設定される Jinja2 環境の3つのフラグを知る必要がある:

| フラグ | 効果 |
| --- | --- |
| `trim_blocks=True` | `{% %}` タグの直後の改行を除去する |
| `lstrip_blocks=True` | `{% %}` タグの行頭の空白を除去する |
| `keep_trailing_newline=True` | テンプレート末尾の改行を保持する |

これにより `{% for %}` / `{% if %}` / `{% endfor %}` の制御行は出力に痕跡を残さない。テンプレートを読むときは「制御行を消した残りが出力される」と考えるとわかりやすい。

## テンプレートに渡されるコンテキスト

```python
{
    "runbook": { ... },        # runbook YAML の runbook セクション全体
    "navigation": { ... },     # runbook.navigation（省略時は {}）
    "params": { ... },         # マージ後の params（dict）
    "region": "ap-northeast-1", # params のフラット展開
    "bucket_name": "...",       # params のフラット展開
    ...
}
```

- `runbook.*` はテンプレート自身が参照する（`runbook.title`、`runbook.operation` 等）
- `params` は 1.1 パラメータ表の生成に使う
- フラット展開された変数はスニペットが参照する（`{{ region }}`、`{{ bucket_name }}` 等）

## セクション別の解説

### ヘッダ部分（1-20行）

```jinja2
# [{{ runbook.id }}] {{ runbook.title }}

## About
{{ runbook.about }}
```

単純な変数展開。`runbook.about` は YAML の `|` ブロックスカラーなので、複数行がそのまま出力される。

`before` / `after` は `{% for %}` でリスト展開し、Markdown の番号付きリストを生成する。すべて `1.` で出力しているが、Markdown のレンダラが自動的に連番にする。

### 1.1 パラメータセクション（29-64行）

テンプレート中で最も複雑な部分。2パスの振り分け処理を行う。

#### パス1: 分類（29-39行）

```jinja2
{% set scalar_params = {} %}
{% set dict_list_params = {} %}
{% for key, value in params.items() %}
  ... 型判定して振り分け ...
{% endfor %}
```

`params` の各値を型で3つに分類する:

| 型 | 判定条件 | 振り分け先 | 表示方法 |
| --- | --- | --- | --- |
| スカラー（文字列/数値） | `value is string or value is number` | `scalar_params` | そのまま表示 |
| 文字列リスト | `value[0] is string` | `scalar_params` | `join(', ')` で結合 |
| 辞書リスト | `value[0] is mapping` | `dict_list_params` | 専用サブテーブル |

`{% set _ = scalar_params.update({key: value}) %}` の書き方について: Jinja2 では `{% do %}` 拡張が無効なため、`update()` の戻り値（`None`）を捨て変数 `_` に代入する形で副作用を起こしている。

#### パス2: 出力（40-64行）

分類済みの辞書をそれぞれループして出力する。

**通常テーブル**（`scalar_params`）:

```
| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
```

**辞書リスト用サブテーブル**（`dict_list_params`）:

```
stack_parameters：

| ParameterKey | ParameterValue |
| --- | --- |
| Environment | `dev` |
```

辞書リスト内の値が配列型の場合は `join(',')` でカンマ区切りに変換する:

```jinja2
{% set display_value = item.value | join(',')
     if item.value is sequence and item.value is not string
     else item.value %}
```

**どちらも空の場合**: 「パラメータなし。」を出力する。

#### なぜ2パスか

通常テーブルを先に、辞書リストのサブテーブルを後にまとめて出す必要がある。1パスで出力すると、通常テーブルの途中にサブテーブルが割り込んでしまう。

### pre_checks セクション（66-77行）

```jinja2
{% for check in runbook.pre_checks or [] %}
#### 1.{{ loop.index + 1 }} {{ check.title }}
```

- `or []` により、`pre_checks` が未定義でもエラーにならない
- `loop.index + 1` で 1.2 から採番（1.1 はパラメータ表が使用）
- `check.description` は `| trim` で末尾の空白を除去
- `{% include check.snippet %}` でスニペットを展開。スニペット内の Jinja2 変数はこの時点で即値に展開される

### 主処理セクション（79-83行）

```jinja2
#### 2.1 リソースの操作 ({{ runbook.operation }})

{% include runbook.main.snippet %}
```

`runbook.operation` が `CREATE` / `MODIFY` / `DELETE` のラベルとして表示される。

### post_checks セクション（85-98行）

pre_checks と対称的な構造。番号は `3.{{ loop.index }}` で 3.1 から採番。

### Navigation セクション（100-105行）

```jinja2
{% if navigation.next %}
#### Navigation

Next: [{{ navigation.next.title }}]({{ navigation.next.link }})
{% endif %}
```

`navigation` が空 dict の場合（YAML で `navigation` キーを省略した場合）、`navigation.next` は `undefined` となり条件は偽になる。シーケンス末尾の手順書では Navigation セクション自体が出力されない。

## 保守時の注意点

### テンプレートを変更すべきケース

- パラメータ表の表示ルールを変更するとき
- セクション構造（前処理/主処理/後処理の骨格）を変更するとき
- 新しい種類のメタ情報（例: 承認者、変更管理番号）を追加するとき

### テンプレートを変更すべきでないケース

- 新しい AWS サービスに対応するとき（スニペットの追加で対応する）
- 新しい操作タイプに対応するとき（YAML の `operation` 値を変えるだけ）
- コマンドの出力例を変えるとき（スニペット側の変更）

### 空行の制御

Markdown では空行がセクション区切りとして重要。テンプレート内の空行の位置は意図的に配置されている。`{% if %}` / `{% endif %}` の前後の空行を不用意に増減すると、生成物の Markdown 構造が崩れる。変更後は必ず生成物を目視確認すること。

### 新しいパラメータ型への対応

現在の分類は「スカラー / 文字列リスト / 辞書リスト」の3種。新しい型（例: ネストした辞書）が必要になった場合は、パス1の分類ロジックに条件を追加し、パス2に対応する出力ブロックを追加する。

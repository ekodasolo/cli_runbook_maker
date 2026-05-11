# generate.py コード解説と保守ガイド

## 概要

`generate.py` は手順書 YAML を読み込み、Jinja2 テンプレートとスニペットを組み合わせて Markdown 手順書を生成する単一ファイルのツール。外部依存は PyYAML と Jinja2 の2つのみ。

## 処理の流れ

```
main()
  ├── argparse で runbook YAML パスを受け取る（複数可）
  ├── build_env() で Jinja2 環境を構築
  └── runbook YAML ごとに render_runbook() を実行
        ├── 1. YAML を読み込み、必須フィールドを検証
        ├── 2. params_files をマージし、runbook.params で上書き
        ├── 3. テンプレートを解決
        ├── 4. コンテキストを構築してレンダリング
        └── 5. dist/ に書き出し
```

## 関数の解説

### `load_yaml(path)`

YAML ファイルを dict として読み込む。空ファイルは `{}` を返す。

### `build_env()`

Jinja2 の `Environment` を構築する。設定値はすべて意図がある:

| 設定 | 値 | 理由 |
| --- | --- | --- |
| `FileSystemLoader` | `ASSETS_ROOT`（`generate.py` と同じディレクトリ） | テンプレート・スニペットを相対パスで参照する |
| `trim_blocks` | `True` | `{% %}` だけの行が空行として残らないようにする |
| `lstrip_blocks` | `True` | `{% %}` 行のインデントを除去する |
| `keep_trailing_newline` | `True` | テンプレート末尾の改行を保持する |

`trim_blocks` と `lstrip_blocks` の組み合わせが重要。これがないと、`{% for %}` や `{% if %}` のある行が空行として出力に残り、Markdown の構造が崩れる。

### `load_params_files(runbook_yaml_path, params_files)`

`params_files` に記述されたパラメータファイルを順に読み込み、マージする。

- パスは **runbook YAML からの相対パス**で解決する（cwd に依存しない）
- マージ順は「記述順、後勝ち」
- 各ファイルはトップレベルに `params:` キーを持つことが必須

### `dist_output_path(runbook_yaml_path)`

runbook YAML のパスから生成物の出力パスを算出する。

```
projects/example/runbooks/0301-create-s3-bucket.yaml
  → projects/example/dist/runbooks/0301-create-s3-bucket.md
```

規約: runbook YAML は `projects/<project>/runbooks/` 直下に置くこと。

### `render_runbook(runbook_yaml_path, env)`

1件の runbook YAML をレンダリングする。コンテキストの構築がポイント:

```python
context = {
    "runbook": runbook,          # YAML の runbook セクション全体
    "navigation": ...,           # navigation セクション
    "params": merged_params,     # マージ後の params（dict として）
    **merged_params,             # params をトップレベルにフラット展開
}
```

`params` を dict として渡す理由: テンプレートの 1.1 パラメータ表で `{% for k, v in params.items() %}` のループに使う。

トップレベルにもフラット展開する理由: スニペット側で `{{ region }}` のように直接参照するため。`{{ params.region }}` と書かせない設計判断。

### `main(argv)`

CLI エントリポイント。終了コードの設計:

| コード | 意味 |
| --- | --- |
| 0 | 全件成功 |
| 1 | 検証エラーまたはテンプレート解決エラー |
| 2 | 指定されたパスが存在しない |

ファイル単位でエラーを報告するが処理は継続する（1件のエラーで残りの生成を止めない）。

## 保守時の注意点

### テンプレート・スニペットの探索パス

`ASSETS_ROOT` は `generate.py` と同じディレクトリに固定されている。`FileSystemLoader` はこのディレクトリをルートとして、`templates/runbook.md.j2` や `snippets/ec2/create-vpc.md` のような相対パスでファイルを探索する。

プロジェクト側からのオーバーライド機構は意図的に持たない。テンプレートを変更したい場合は共通資産そのものを修正する。

### params_files のパス解決

`load_params_files` 内のパス解決は runbook YAML の位置基準。`../params/training-s3.yaml` は「runbook YAML があるディレクトリの1つ上の `params/` ディレクトリ」を意味する。

これにより、どのディレクトリから `python generate.py` を実行しても同じ結果になる。

### Jinja2 Environment の拡張

現在はカスタムフィルタやグローバル関数を登録していない。将来 `StrictUndefined` への切り替えが検討されている（未定義変数の検出用）。切り替え時は、テンプレート内の `{% if check.description %}` のような optional フィールドアクセスを `{% if 'description' in check %}` に書き換える必要がある。

### エラーメッセージの言語

コメントは日本語、エラーメッセージと argparse help は英語。スタックトレースでの文字化けリスク回避と `--help` の国際的可読性のための方針。

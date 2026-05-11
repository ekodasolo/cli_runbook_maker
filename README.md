# CLI Runbook Maker

AWS CLI 作業手順書（Runbook）の生成ツールキット。

YAML 定義ファイルから、人間が CloudShell で読みながら対話的にコマンドを実行するための Markdown 手順書を生成する。

## 何ができるか

- **YAML を書くだけで手順書を量産できる**。テンプレートとスニペットが構造・コマンド・結果例を提供するため、YAML 側はパラメータと構成を定義するだけで済む
- **即値レンダリング**。生成された手順書のコマンドはすべてリテラル値で展開されるため、画面に表示されているコマンドをそのままコピー&ペーストで実行できる
- **スニペットの再利用**。1つの AWS CLI コマンドに対応するスニペットを、複数の手順書の事前確認・主処理・事後確認で使い回せる

## 対応サービス

| サービス | スニペット | ランブック例 |
| --- | --- | --- |
| EC2 (VPC) | 22 | 2 |
| SSM Parameter Store | 6 | 4 |
| S3 | 13 | 6 |
| KMS | 8 | 3 |
| CloudFormation | 8 | 4 |
| DynamoDB | 6 | 3 |

## セットアップ

```bash
pip install -r requirements.txt
```

依存パッケージは PyYAML と Jinja2 の2つのみ。

## 使い方

### 手順書の生成

```bash
python generate.py <runbook.yaml> [<runbook.yaml> ...]
```

複数ファイルを指定すると一括生成する。

```bash
# 1件だけ生成
python generate.py examples/runbooks/0301-create-s3-bucket.yaml

# 全件一括生成
python generate.py examples/runbooks/*.yaml
```

生成物は `<project>/dist/runbooks/<basename>.md` に出力される。

### 新しい手順書の作り方

#### 1. スニペットを用意する

`snippets/{service}/` に、1つの AWS CLI コマンドに対応する Markdown ファイルを配置する。

```markdown
バケットのバージョニング設定を確認する。

```bash
aws s3api get-bucket-versioning \
    --bucket {{ bucket_name }} \
    --region {{ region }}
```

結果の例
```output
{
    "Status": "Enabled"
}
```
```

`{{ bucket_name }}` のような Jinja2 変数は、生成時にパラメータ値で即値に展開される。

#### 2. 共通パラメータファイルを用意する

複数の手順書で共有する値を YAML にまとめる。

```yaml
# examples/params/training-s3.yaml
params:
  region: ap-northeast-1
  bucket_name: project-dev-training-bucket
```

#### 3. 手順書 YAML を書く

```yaml
runbook:
  id: "0301"
  title: "S3 バケットを作成する"
  about: |
    S3 バケット作成の CLI 手順書。
  operation: CREATE
  template: runbook

  before:
    - 同名のバケットがまだ作成されていないこと。
  after:
    - バケットが作成されていること。

  pre_checks:
    - title: "同名バケットの非存在確認"
      description: |
        作成対象のバケットがまだ存在しないことを確認する。
      snippet: snippets/s3/head-bucket.md

  main:
    snippet: snippets/s3/create-bucket.md

  post_checks:
    - title: "バケットの作成確認"
      description: |
        バケットが正常に作成されたことを確認する。
      snippet: snippets/s3/head-bucket.md

  params_files:
    - ../params/training-s3.yaml

  params: {}

  navigation:
    next:
      title: "S3 バケットのバージョニングを有効にする"
      link: "./0302-enable-s3-versioning.md"
```

#### 4. 生成して確認する

```bash
python generate.py examples/runbooks/0301-create-s3-bucket.yaml
```

## ディレクトリ構成

```
cli_runbook_maker/
  generate.py                     # 生成ツール本体
  templates/
    runbook.md.j2                 # 汎用テンプレート（1ファイルのみ）
  snippets/
    {service}/                    # サービスごとにディレクトリを分割
      {aws-cli-subcommand}.md     # 1スニペット = 1 AWS CLI コマンド
  examples/                       # サンプルプロジェクト
    params/                       # 共通パラメータ（サービスドメイン単位）
      training-s3.yaml
      training-kms.yaml
      ...
    runbooks/                     # 手順書 YAML 定義
      0301-create-s3-bucket.yaml
      0302-enable-s3-versioning.yaml
      ...
    dist/runbooks/                # 生成物（Markdown）
      0301-create-s3-bucket.md
      0302-enable-s3-versioning.md
      ...
```

## 生成される手順書の構造

```
# [ID] タイトル
## About                          ... 手順の概要
## When: 作業の条件
  ### Before: 事前前提条件         ... 作業前に満たすべき条件
  ### After: 作業終了状況          ... 完了の判定基準
## How: 以下は作業手順
  ### 1. 前処理
    #### 1.1 処理パラメータ        ... パラメータ一覧表
    #### 1.2 [事前確認タイトル]    ... pre_checks（複数可）
  ### 2. 主処理
    #### 2.1 リソースの操作 (CREATE/MODIFY/DELETE)
  ### 3. 後処理
    #### 3.1 [事後確認タイトル]    ... post_checks（複数可）
  #### Navigation                 ... 次の手順書へのリンク（任意）
# EOD
```

## 設計の詳細

- 仕様: [SPEC.md](SPEC.md)
- 開発パターンと TIPS: [KNOWLEDGE.md](KNOWLEDGE.md)

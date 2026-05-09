# Runbook Toolkit 仕様書

## 1. 概要

AWS CLI作業手順書の作成を効率化するツールキット。

手順書は人間がCloudShell上で読みながら対話的にコマンドを実行するためのものであり、この運用は変えない。ツールキットは手順書の「書く側の労力」を削減することを目的とする。

### 1.1 設計思想

- 手順書は人間が読んで文脈を理解しながら対話的に実行するもの。スクリプトで自動実行するものではない。
- Why（なぜその作業をするか）や前提条件は省略できない。人が交代しても意味がわかる手順書を維持する。
- 操作タイプごとのテンプレートとスニペットを資産として蓄積し、新しい手順書はYAML定義だけで量産可能にする。


## 2. 3層構造

手順書を以下の3層で組織化する。

### 2.1 シナリオ（Scenario）

- 1つ以上の手順書から構成される作業の全体像
- Why（目的）、What（対象）、Who（前提スキル）、Where（作業環境）を記述する
- 手順書の実行順序と共通パラメータを定義する
- 例：「S3バケットを作成してバージョニングを有効にする」

### 2.2 手順書（Runbook）

- 1つのリソース操作に対応する手順
- Before/After条件、使用テンプレート、固有パラメータを定義する
- 構造は前処理（事前確認）→ 主処理（リソース操作）→ 後処理（事後確認）で統一する
- 例：「VPCを作成する」「DNS Hostnameを有効にする」

### 2.3 スニペット（Snippet）

- 1つのAWS CLIコマンドのテンプレート
- 純粋にコマンドの内容だけを持つ。役割（事前確認・実行・事後確認）は知らない
- 役割の割り当てはテンプレート側が制御する
- 例：`ec2/create-vpc.md`、`ssm/put-parameter.md`


## 3. ファイル構成

### 3.1 共通資産リポジトリ（runbook-toolkit）

業務横断で共有・蓄積するもの。

```
runbook-toolkit/
├── snippets/                       # コマンドスニペット
│   ├── ec2/
│   │   ├── create-vpc.md
│   │   ├── describe-vpcs.md
│   │   ├── describe-vpc-attribute.md
│   │   └── modify-vpc-attribute.md
│   ├── ssm/
│   │   ├── put-parameter.md
│   │   └── describe-parameters.md
│   └── s3/
│       └── ...
├── templates/                      # 手順書テンプレート（デフォルト）
│   ├── ec2-create-vpc.md.j2
│   └── ec2-modify-vpc-attribute.md.j2
├── generate.py                     # 生成ツール
├── SPEC.md                         # 本ドキュメント
└── README.md
```

### 3.2 プロジェクトリポジトリ（業務ごと）

プロジェクト固有の定義と生成物を配置する。

```
project-xxx/
├── scenarios/
│   ├── 0100-create-vpc.yaml        # シナリオ定義
│   └── 0100-create-vpc.md          # ← 生成物
├── runbooks/
│   ├── 0101-create-vpc.yaml        # 手順書定義
│   ├── 0101-create-vpc.md          # ← 生成物
│   ├── 0102-modify-dns-hostname.yaml
│   └── 0102-modify-dns-hostname.md # ← 生成物
└── templates/                      # オーバーライド（任意）
    └── ...
```

### 3.3 テンプレート解決順序

生成ツールがテンプレートを探すとき、以下の優先順位で解決する。

1. プロジェクト側の `templates/`（あれば優先）
2. 共通資産側の `templates/`（フォールバック）

### 3.4 生成物のgit管理

生成された `.md` ファイルはgitにコミットする。生成ツールがなくても手順書として読めることを保証するため。


## 4. YAML定義フォーマット

### 4.1 シナリオYAML

```yaml
scenario:
  id: "0100"
  title: "Training用VPCの作成"
  description: |
    基本的なVPC構成によるネットワークを構築する。
    本シナリオでは、VPCを作成する。
  who:
    - Unixシェルの基本操作ができること
    - AWS CLIの基本操作ができること
    - EC2/VPCへのアクセス権があること
  where: |
    CloudShellに接続し、CloudShell上で作業することを前提とする。

  # シナリオ共通パラメータ（各手順書に注入される）
  params:
    region: ap-northeast-1
    vpc_cidr: "10.0.0.0/24"
    vpc_name: "project-dev-main-vpc"

  steps:
    - runbook: 0101-create-vpc
    - runbook: 0102-modify-dns-hostname
```

### 4.2 手順書YAML

```yaml
runbook:
  id: "0101"
  title: "VPCを作成する"
  about: |
    VPCを東京リージョンに作成する。
  services:
    - EC2/VPC
  duration: "5 Min"

  before:
    - 作業リージョンでVPCの作成数上限に達しておらずVPCが作成可能である。
    - 割り当てたIPアドレス範囲が他の既存のVPCと重複しておらず、作成可能である。
  after:
    - VPCが作成されている。
    - 作成したVPCは東京リージョンに配置されている。

  # 使用するテンプレート
  template: ec2-create-vpc

  # この手順書固有のパラメータ（任意）
  params: {}
```

手順書固有のパラメータがある場合の例：

```yaml
runbook:
  id: "0102"
  title: "VPC属性を設定する"
  about: |
    VPCの属性値を変更し、DNS Hostnameを有効にする。

  before:
    - VPCが作成済みである。
    - VPCの属性値DNS hostnameがDisabledになっている。
  after:
    - VPCのDNS hostnamesが、Enabledになっている。

  template: ec2-modify-vpc-attribute

  params:
    attribute: enableDnsHostnames
    value: true
```


## 5. パラメータ解決

### 5.1 マージ順序

```
シナリオ共通 params（ベース）
  ↓ マージ
手順書固有 params（上書き）
  ↓ 注入
テンプレート（Markdown + Jinja2）
  ↓ 展開
スニペット（コマンド断片）
```

手順書固有のparamsがシナリオ共通paramsと同じキーを持つ場合、手順書側が優先される。


## 6. テンプレート仕様

### 6.1 形式

Markdown + Jinja2。テンプレートを見れば生成されるMarkdownの構造がそのまま見える。

### 6.2 テンプレートからスニペットの利用

テンプレート内で `{% include %}` を使ってスニペットを展開する。
スニペットにはテンプレート変数が渡され、プレースホルダが解決される。

### 6.3 テンプレートの責務

- 前処理・主処理・後処理の構造を定義する
- どのスニペットをどの役割（事前確認・実行・事後確認）で配置するかを制御する
- ループ展開（複数リソースの一括操作）を行う

### 6.4 スニペットの責務

- 1つのAWS CLIコマンドとその説明、期待される出力例を持つ
- 変数のプレースホルダを含む
- 役割や実行順序は関知しない


## 7. 生成ツール（generate.py）

### 7.1 実行方法

```bash
# シナリオ単位で生成（配下の全手順書も生成される）
python generate.py \
    --toolkit /path/to/runbook-toolkit \
    --scenario scenarios/0100-create-vpc.yaml

# 将来的にはCLIツールとしてインストール可能にする
# pip install runbook-toolkit
# runbook generate --scenario scenarios/0100-create-vpc.yaml
```

### 7.2 生成物

- シナリオMarkdown：手順書一覧と概要
- 手順書Markdown：CloudShellで読みながら実行できる完全な手順書

生成される手順書のフォーマットは、現行の手順書と同等の品質・構造を維持する。


## 8. 操作タイプの拡充計画

テンプレートとスニペットは操作タイプごとに順次追加する。

初期スコープ：
- EC2/VPC: VPC作成、VPC属性変更
- SSM: パラメータ作成

追加予定：
- S3: バケット作成、バージョニング設定
- KMS: キー作成
- CloudFormation: スタック操作


## 9. 生成されるMarkdownの構造

生成物は以下の統一構造に従う（現行手順書と同じ）。

```
# [XXXX] タイトル

## About
## When: 作業の条件
### Before: 事前前提条件
### After: 作業終了状況
## How: 以下は作業手順
### 1. 前処理
#### 1.1 処理パラメータの準備
#### 1.2 事前条件Nの確認
### 2. 主処理
#### 2.1 リソースの操作 (CREATE/MODIFY/DELETE)
### 3. 後処理
#### 3.1 完了条件Nの結果確認
#### 3.99 中間リソースの削除
#### Navigation
# EOD
```

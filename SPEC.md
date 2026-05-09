# Runbook Toolkit 仕様書

## 1. 概要

AWS CLI作業手順書の作成を効率化するツールキット。

手順書は人間がCloudShell上で読みながら対話的にコマンドを実行するためのものであり、この運用は変えない。ツールキットは手順書の「書く側の労力」を削減することを目的とする。

### 1.1 設計思想

- 手順書は人間が読んで文脈を理解しながら対話的に実行するもの。スクリプトで自動実行するものではない。
- Why（なぜその作業をするか）や前提条件は省略できない。人が交代しても意味がわかる手順書を維持する。
- 操作タイプごとのテンプレートとスニペットを資産として蓄積し、新しい手順書はYAML定義だけで量産可能にする。
- 仕組みはできるだけ単純に保つ。階層・抽象・拡張ポイントは必要になってから追加する。


## 2. 2層構造

手順書を以下の2層で組織化する。

### 2.1 手順書（Runbook）

- 1つのリソース操作に対応する手順
- About、Before/After条件、使用テンプレート、パラメータ、後続手順書へのナビゲーションを定義する
- 構造は前処理（事前確認）→ 主処理（リソース操作）→ 後処理（事後確認）で統一する
- 例：「VPCを作成する」「DNS Hostnameを有効にする」

### 2.2 スニペット（Snippet）

- 1つのAWS CLIコマンドのテンプレート
- 純粋にコマンドの内容だけを持つ。役割（事前確認・実行・事後確認）は知らない
- 役割の割り当てはテンプレート側が制御する
- 例：`ec2/create-vpc.md`、`ssm/put-parameter.md`

> 補足：以前は「シナリオ（複数手順書をまとめる上位層）」を3層目として置いていたが、運用上は手順書一覧を README 等のドキュメントで示せば十分であり、層を1つ減らした。共通パラメータは §5.2 の `params_files` で扱う。


## 3. リポジトリ構造

ツールキット（テンプレート・スニペット・ジェネレータ）と、各業務固有のYAML定義・生成物は同一リポジトリに同居する。リポジトリを分けない単純構成を採る。

```
cli_runbook_maker/
├── generate.py                     # 生成ツール
├── requirements.txt
├── snippets/                       # コマンドスニペット
│   └── ec2/
│       ├── create-vpc.md
│       ├── describe-vpcs.md
│       ├── describe-vpc-attribute.md
│       └── modify-vpc-attribute.md
├── templates/                      # 手順書テンプレート
│   ├── ec2-create-vpc.md.j2
│   └── ec2-modify-vpc-attribute.md.j2
├── examples/                       # サンプル兼検証用プロジェクト
│   ├── params/
│   │   └── training-common.yaml    # 共通パラメータ
│   ├── runbooks/
│   │   ├── 0101-create-vpc.yaml    # 手順書定義
│   │   └── 0102-modify-dns-hostname.yaml
│   └── dist/                       # 生成物
│       └── runbooks/
│           ├── 0101-create-vpc.md
│           └── 0102-modify-dns-hostname.md
├── SPEC.md
├── TASKS.md
├── LOGS.md
├── CLAUDE.md
└── README.md
```

### 3.1 ディレクトリの役割

| ディレクトリ | 役割 |
| --- | --- |
| `templates/` | 手順書テンプレート（共通資産） |
| `snippets/` | AWS CLI コマンドスニペット（共通資産） |
| `<project>/runbooks/` | 業務ごとの手順書 YAML 定義 |
| `<project>/params/` | 業務ごとの共通パラメータ YAML（任意） |
| `<project>/dist/runbooks/` | 業務ごとの手順書 Markdown 生成物 |

`<project>` は、`runbooks/` を含む任意のディレクトリ。リポジトリ内では `examples/` がそれに相当する。将来的に他業務の手順書を追加する場合は `clientA/`, `internal/` 等を兄弟ディレクトリとして並べる。

### 3.2 テンプレート・スニペットの探索

`generate.py` と同じディレクトリ配下の `templates/` と `snippets/` のみを参照する。プロジェクト側のオーバーライド機構は持たない。テンプレートに修正を入れたい場合は、共通資産そのものを変更するか、新しいテンプレートとして追加する。

### 3.3 生成物のgit管理

生成された `.md` ファイルはgitにコミットする。生成ツールがなくても手順書として読めることを保証するため。


## 4. YAML定義フォーマット

### 4.1 手順書YAML

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

  # 使用するテンプレート（templates/<value>.md.j2 を参照）
  template: ec2-create-vpc

  # 共通パラメータファイル（任意、複数指定可・上から順にマージ）
  params_files:
    - ../params/training-common.yaml

  # この手順書固有のパラメータ（params_files より優先）
  params: {}

  # 後続手順書へのリンク（任意、Navigation セクションに展開）
  navigation:
    next:
      id: "0102"
      title: "VPC属性を設定する"
      link: "./0102-modify-dns-hostname.md"
```

固有パラメータがある場合の例：

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

  params_files:
    - ../params/training-common.yaml

  params:
    attribute: enableDnsHostnames
    cli_option: enable-dns-hostnames
    value: true
```

### 4.2 共通パラメータYAML

```yaml
# examples/params/training-common.yaml
params:
  region: ap-northeast-1
  vpc_cidr: "10.0.0.0/24"
  vpc_name: "project-dev-main-vpc"
```

トップレベルの `params` キーの直下にフラットな key-value を並べる。`params_files` で複数指定された場合は記述順にマージし、後勝ちで上書きされる。


## 5. パラメータ解決

### 5.1 マージ順序

```
runbook.params_files[0].params（ベース）
  ↓ マージ（後勝ち）
runbook.params_files[1].params
  ↓ マージ（後勝ち）
...
runbook.params（最優先）
  ↓ 注入
テンプレート（Markdown + Jinja2）
  ↓ 展開
スニペット（コマンド断片）
```

### 5.2 共通パラメータの単位

`params_files` は「複数の手順書で共有したい値」を切り出すための機構。シナリオ層を持たない代わりに、共有粒度を runbook YAML 側で明示的に選択させる。1ファイルに全部入れてもよいし、業務単位・環境単位で分割してもよい。


## 6. テンプレート仕様

### 6.1 形式

Markdown + Jinja2。テンプレートを見れば生成されるMarkdownの構造がそのまま見える。

### 6.2 テンプレートからスニペットの利用

テンプレート内で `{% include %}` を使ってスニペットを展開する。スニペットにはテンプレート変数が渡され、プレースホルダが解決される。

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
# 1つの手順書を生成
python generate.py examples/runbooks/0101-create-vpc.yaml

# 複数指定（順序自由、まとめて生成）
python generate.py examples/runbooks/*.yaml
```

引数は手順書YAMLのパスのみを受け取る。テンプレート・スニペットは `generate.py` と同じディレクトリ配下から参照する（`--toolkit` 等のフラグは持たない）。

### 7.2 出力先

```
<runbook_yaml>          → <runbook_yaml.parent.parent>/dist/runbooks/<basename>.md
```

例：`examples/runbooks/0101-create-vpc.yaml` → `examples/dist/runbooks/0101-create-vpc.md`

定義（YAML）と生成物（MD）は完全に分離し、`dist/` 配下に runbooks/ の構造をミラーして配置する。

### 7.3 生成物

CloudShellで読みながら実行できる完全な手順書Markdown。フォーマットは現行の手順書と同等の品質・構造を維持する。


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

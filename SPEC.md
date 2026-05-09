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
    VPCを作成するCLI手順書。

    本手順では、VPCを東京リージョンに作成する。
  services:
    - EC2/VPC
  duration: "5 Min"
  operation: CREATE              # 操作タイプラベル（CREATE / MODIFY / DELETE 等）

  before:
    - 作業リージョンでVPCの作成数上限に達しておらずVPCが作成可能である。
  after:
    - VPCが作成されている。

  # 使用するテンプレート（templates/<value>.md.j2 を参照）
  # 通常は汎用テンプレート "runbook" を使う
  template: runbook

  # 1.2, 1.3, ... の事前確認ブロック（順序通り展開される）
  # title は必須。description / snippet は任意
  pre_checks:
    - title: "VPC作成数の上限の確認"
      description: |
        リージョン内に作成できるVPCの数は、上限緩和していなければ5個まで。
      snippet: snippets/ec2/list-vpcs.md
    - title: "依存リソースの確認"
      description: 依存するリソースは無い。

  # 2.1 主処理に展開するスニペット
  main:
    snippet: snippets/ec2/create-vpc.md

  # 3.1 事後確認に展開するスニペット（複数可）
  post_checks:
    - snippet: snippets/ec2/describe-vpcs.md

  # 共通パラメータファイル（任意、複数指定可・上から順にマージ）
  params_files:
    - ../params/training-common.yaml

  # この手順書固有のパラメータ（params_files より優先）
  params: {}

  # 後続手順書へのリンク（任意、Navigation セクションに展開）
  navigation:
    next:
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
  operation: MODIFY

  before:
    - VPCが作成済みである。
  after:
    - VPCのDNS hostnamesが Enabled になっている。

  template: runbook

  pre_checks:
    - title: "VPCが作成済みであることの確認"
      snippet: snippets/ec2/find-vpc-id-by-cidr.md
    - title: "VPC属性の現状確認"
      snippet: snippets/ec2/describe-vpc-dns-attributes.md

  main:
    snippet: snippets/ec2/modify-vpc-attribute.md

  post_checks:
    - snippet: snippets/ec2/describe-vpc-attribute.md

  params_files:
    - ../params/training-common.yaml

  params:
    attribute: enableDnsHostnames
    cli_option: enable-dns-hostnames
    value: "true"            # JSON リテラルに合わせて文字列で書く（§6.7）
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

### 6.2 汎用テンプレートの方針

テンプレートは操作タイプ × 特定リソースで増殖させない。リソースに依らない構造（前処理／主処理／後処理の骨格、§9 のセクション構成）は **単一の汎用テンプレート `templates/runbook.md.j2`** に集約する。リソース固有のコマンドはスニペット側に置き、runbook YAML が「どのスニペットを、どの役割で並べるか」を宣言する。

新しいリソースタイプ（例：S3、KMS）を追加するときは、原則としてスニペットを増やすだけで済み、テンプレート本体は変更しない。

### 6.3 テンプレートからスニペットの利用

テンプレート内で `{% include %}` を使ってスニペットを展開する。スニペットには runbook YAML の `params` がフラットにコンテキストとして渡され、Jinja2 のプレースホルダが解決される。

### 6.4 テンプレートの責務

- §9 の統一構造（前処理・主処理・後処理）の骨格を定義する
- runbook YAML の `pre_checks[]` / `main` / `post_checks[]` を宣言された順序に展開する
- マージ後の `params` から 1.1 のパラメータ表（キー・値の表）を生成する
- セクション番号（1.1, 1.2, ...）の自動採番を行う

### 6.5 スニペットの責務

- 1つの目的に対応する AWS CLI コマンドとその説明・期待される出力例を持つ
  - 1コマンドが原則だが、関連する一連のコマンド（例：「VPC を確認し ID をシェル変数に取得する」）を1スニペットにまとめてよい
- 役割（事前確認 / 主処理 / 事後確認）や実行順序は関知しない。役割は runbook YAML が指定する

### 6.6 スニペット内の変数規約（即値原則）

手順書は生成されるものなので、コマンドの値は基本的に **即値で書き出す**。読み手は手元の画面に出ているコマンドそのものが「これから流れる／流したコマンド」だと信じてよい。シェル変数で抽象化するのは、生成時には確定しない値（実行時に AWS から取得する VPC ID 等）に限る。

| 値の種類 | 例 | スニペット内の表記 | 出力例 |
| --- | --- | --- | --- |
| **静的設定**（YAML から確定） | region、vpc_cidr、vpc_name、attribute、cli_option、value | Jinja2 `{{ region }}` | `--region ap-northeast-1` |
| **実行時取得**（pre_check で AWS から取得） | VPC_ID、SUBNET_ID 等 | シェル変数 `${VPC_ID}` | `--vpc-id ${VPC_ID}` |

例（`snippets/ec2/modify-vpc-attribute.md`）：

```bash
aws ec2 modify-vpc-attribute \
    --vpc-id ${VPC_ID} \                           # 実行時取得 → シェル変数
    --{{ cli_option }} "{\"Value\":{{ value }}}" \  # 静的 → Jinja2 即値
    --region {{ region }}                          # 静的 → Jinja2 即値
```

例示出力（`結果の例`）も Jinja2 で展開してよい。実 runbook の値が結果例に反映されるとリアル化し、読み手が実際の出力と比較しやすい。

### 6.7 値の YAML 表記の規約

JSON リテラルとしてコマンドに埋め込まれるパラメータ（`value` 等）は、**JSON リテラルそのものに一致する文字列で書く**:

```yaml
params:
  value: "true"     # JSON で "true" と書きたいので YAML でも "true"（文字列）
  # NG: value: true   ← Python の bool になり、Jinja2 経由で "True" になる
  # NG: value: 30     ← 数値はそのまま動くが、整合性のため "30" 推奨
```

理由：YAML の bool/int をそのまま使うと、Python の str() 規則で `True`／`False` のように大文字化され、JSON リテラル（`true`／`false`）と一致しなくなる。1.1 のパラメータ表とコマンド本体での表記を一致させるためにも、文字列指定を推奨する。


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

手順書本体のテンプレート（汎用）は1個に固定し（§6.2）、リソース対応の拡充は **スニペット追加** で行う。

初期スコープ（実装済み）：
- 汎用テンプレート: `templates/runbook.md.j2`
- EC2/VPC スニペット:
  - `snippets/ec2/list-vpcs.md` — VPC 一覧（事前確認向け）
  - `snippets/ec2/find-vpc-id-by-cidr.md` — CIDR で VPC を検索し、ID をシェル変数に取得
  - `snippets/ec2/describe-vpcs.md` — VPC 詳細を CIDR で確認（事後確認向け）
  - `snippets/ec2/describe-vpc-attribute.md` — VPC 属性確認（汎用、`${ATTRIBUTE}` 指定）
  - `snippets/ec2/describe-vpc-dns-attributes.md` — DNS 関連 VPC 属性確認
  - `snippets/ec2/create-vpc.md` — VPC 作成
  - `snippets/ec2/modify-vpc-attribute.md` — VPC 属性変更（汎用、`${CLI_OPTION}` `${VALUE}` 指定）

追加予定：
- SSM: パラメータ作成、パラメータ取得
- S3: バケット作成、バージョニング設定
- KMS: キー作成
- CloudFormation: スタック操作


## 9. 生成されるMarkdownの構造

生成物は以下の統一構造に従う。

```
# [XXXX] タイトル

## About
## When: 作業の条件
### Before: 事前前提条件
### After: 作業終了状況
## How: 以下は作業手順
### 1. 前処理
#### 1.1 処理パラメータ              ← パラメータ表（キー・値）
#### 1.2 事前条件Nの確認             ← pre_checks[] が 1.2, 1.3, ... と展開
### 2. 主処理
#### 2.1 リソースの操作 (CREATE/MODIFY/DELETE)
### 3. 後処理
#### 3.1 完了条件の結果確認          ← After 条件 + post_checks[]
#### Navigation                      ← navigation.next がある場合のみ
# EOD
```

### 9.1 1.1 処理パラメータ

マージ済みの `params` から自動生成される表。例：

```
| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| vpc_cidr | `10.0.0.0/24` |
| vpc_name | `project-dev-main-vpc` |
```

旧仕様にあったシェル変数代入ブロック（`AWS_REGION="ap-northeast-1"` 等）は廃止。コマンドは即値で出力されるため、シェル変数で抽象化する必要がない（§6.6）。

# Runbook Toolkit 作業ログ

## 2025-02-26: サンプルYAML作成

### 実施内容
- シナリオYAML作成: `examples/scenarios/0100-create-vpc.yaml`
- 手順書YAML作成: `examples/runbooks/0101-create-vpc.yaml`
- 手順書YAML作成: `examples/runbooks/0102-modify-dns-hostname.yaml`

### 決定事項
- `navigation`（次の手順書へのリンク）は手順書YAML側に配置した
- `cli_option`（CLIオプション名）と`attribute`（API属性名）を分離し、手順書固有paramsとして定義する方針とした（0102の例: `attribute: enableDnsHostnames`, `cli_option: enable-dns-hostnames`）


## 2025-02-26: スニペット・テンプレート作成

### 実施内容
- EC2/VPC関連のスニペット4件を作成
  - `snippets/ec2/create-vpc.md`
  - `snippets/ec2/describe-vpcs.md`
  - `snippets/ec2/describe-vpc-attribute.md`
  - `snippets/ec2/modify-vpc-attribute.md`
- 手順書テンプレート2件を作成
  - `templates/ec2-create-vpc.md.j2`
  - `templates/ec2-modify-vpc-attribute.md.j2`

### 決定事項
- スニペット内ではJinja2の複雑なフィルター変換を避け、テンプレート側から適切な値を渡す方針とした
  - 例: `modify-vpc-attribute`のCLIオプション名（`enable-dns-hostnames`）は`cli_option`として明示的に渡す
  - `attribute`（API名: `enableDnsHostnames`）と`cli_option`（CLI名: `enable-dns-hostnames`）の変換責任はテンプレート/YAML側に持たせる
- スニペットのincludeは主処理の実行コマンドと事後確認で使用し、事前確認やパラメータ準備などコンテキスト依存の部分はテンプレート内に直書きとした
  - 事前確認のdescribe-vpcsは`--query`付き簡易一覧など使い方が異なるため
  - VPC ID取得などの中間ステップはテンプレートの責務として直書き


## 2025-02-26: 初期設計

### 実施内容
- CLI手順書の課題分析とディスカッション
- 3層構造（シナリオ・手順書・スニペット）の設計決定
- ファイル構成の決定（共通資産リポジトリ / プロジェクトリポジトリの分離）
- YAML定義フォーマットの決定
- パラメータ解決順序の決定
- テンプレート形式の決定（Markdown + Jinja2）
- SPEC.md 作成・承認

### 決定事項
- 手順書の最終形はMarkdownで、CloudShellで対話的に実行する運用は変えない
- スニペットは純粋なコマンドテンプレート。役割はテンプレート側が制御する
- テンプレートはMarkdown + Jinja2。宣言的YAMLではなく、最終出力が見える形式を採用
- シナリオ側に共通パラメータを持ち、各手順書に注入する
- テンプレート解決はプロジェクト側優先、共通側フォールバック
- 生成物のMarkdownはgitにコミットする

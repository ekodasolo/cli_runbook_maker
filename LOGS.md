# Runbook Toolkit 作業ログ

## 2026-05-09: ドキュメント矛盾の修正

### 実施内容
- CLAUDE.md のタスク管理ファイル名を実体に合わせて `TODOS.md` → `TASKS.md` に修正
- CLAUDE.md に LOGS.md の運用ルールを追記
- Jinjaテンプレートの拡張子を SPEC.md の規定どおり `.j2.txt` → `.j2` に揃えた

### 決定事項
- 作業ログの構成は「日付見出し → 実施内容 → 決定事項」で統一する


## 2026-05-09: 生成ツール (generate.py) の基本実装

### 実施内容
- `generate.py` を実装。シナリオYAMLを起点に手順書MDとシナリオサマリーMDを生成する
- シナリオMD用テンプレート `templates/scenario.md.j2` を新設
- 依存関係を `requirements.txt`（PyYAML, Jinja2）に固定。`.tool-versions` で Python 3.13.12 を固定
- VPC作成シナリオで動作確認：`examples/scenarios/0100-create-vpc.md` ほか2件の手順書MDを生成

### 決定事項
- テンプレート/スニペット解決は Jinja2 `FileSystemLoader([project_root, toolkit_root])` で実現。プロジェクト側を先に登録することで SPEC §3.3 のオーバーライド優先順位を自然に表現
- スニペットの include はテンプレートからの相対パス（`snippets/ec2/create-vpc.md`）で参照する。Loader の検索パス設計と整合
- パラメータ解決の context は `{ runbook, scenario, navigation, **merged_params }` の構造とし、テンプレートからは `{{ region }}` のように params をフラットに参照できるようにした
- `trim_blocks=True, lstrip_blocks=True` を採用。インラインの `{% endif %}` が行末に来ると直後の改行を消費する挙動が判明したため、シナリオテンプレートでは `{% set %}` で変数化して回避
- 生成物 `.md` は SPEC §3.4 に従い git にコミットする
- テンプレート側の既知課題（`vpc_id` 未定義、日本語タイトルからの `RUNBOOK_TITLE` 生成）は generate.py の責務外として TASKS.md に切り出した


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

# Runbook Toolkit タスクリスト

## フェーズ0: 仕様の簡素化 — 完了

3層構造（シナリオ／手順書／スニペット）から2層構造（手順書／スニペット）に変更し、ツールキット／プロジェクトのリポジトリ分離も廃止した。詳細は SPEC.md 参照。

### 仕様ドキュメントの刷新
- [✓] SPEC.md の刷新（2層構造、シングルリポジトリ、`params_files` 機構、新CLI）
- [✓] TASKS.md の刷新（本ファイル）
- [✓] LOGS.md に簡素化方針の決定を記録

### 実装の追従（feature/cli-simplification）
- [✓] `generate.py` のCLI簡素化
  - [✓] 位置引数で runbook YAML を受け取り（複数可）、`--toolkit`／`--scenario` を廃止
  - [✓] テンプレート・スニペットの探索パスを `generate.py` 隣接ディレクトリに固定
  - [✓] `params_files` フィールドの読み込みとマージ順の実装
  - [✓] 出力先を `<runbook>.parent.parent/dist/runbooks/<basename>.md` に変更
- [✓] `templates/scenario.md.j2` を削除
- [✓] `examples/scenarios/` を削除（手順書一覧の提示は今後 README 等で行う）
- [✓] 旧 `examples/scenarios/0100-create-vpc.yaml` の `params:` を `examples/params/training-common.yaml` に移設
- [✓] `examples/runbooks/*.yaml` に `params_files: [../params/training-common.yaml]` を追記
- [✓] 動作検証：新CLIで `examples/runbooks/*.yaml` を生成し、`examples/dist/runbooks/*.md` が以前と完全一致（`diff -u` で差分なし）することを確認

備考：
- `0101-create-vpc.yaml` の `navigation.next` は元から runbook YAML 側に存在していたため移設不要だった
- 旧 generate.py のシナリオ MD 出力は廃止。フェーズ1の「シナリオMD生成成功」の検証項目はもう該当しない

---

## フェーズ1.5: テンプレート汎化 — 完了

テンプレートが「操作タイプ × 特定リソース」で1対1に貼り付き、新リソースを追加するたびに新テンプレートが要る状態（SPEC §1.1 の「資産として蓄積」方針に反する）を解消した。汎用テンプレート1個 + 役割中立スニペットの組合せに移行済み。

### 設計
- [✓] 汎用テンプレート `templates/runbook.md.j2` を新設（CREATE/MODIFY/DELETE 共通）
- [✓] runbook YAML スキーマに `slug` / `operation` / `shell_vars` / `pre_checks[]` / `main` / `post_checks[]` を導入（SPEC §4.1 更新）
- [✓] スニペット内の変数規約を確立（コマンド本体はシェル変数、例示出力は Jinja 変数。SPEC §6.6 で明文化）
- [✓] パラメータプレビュー（`cat << EOF > $FILE_PARAMETER`）ブロックは廃止 — 0102 で破綻していたため
- [✓] 1.1 の `RUNBOOK_TITLE` を `slug` から生成（既知課題「日本語タイトルが混入」を解消）

### 実装
- [✓] `templates/runbook.md.j2` を作成（pre_checks/post_checks の自動採番、shell_vars ループ展開）
- [✓] スニペット新設：`list-vpcs.md` / `find-vpc-id-by-cidr.md` / `describe-vpc-dns-attributes.md`
- [✓] 既存スニペット書き換え（コマンドをシェル変数化）：`create-vpc.md` / `describe-vpcs.md` / `modify-vpc-attribute.md` / `describe-vpc-attribute.md`
- [✓] `examples/runbooks/0101-create-vpc.yaml` を新スキーマに移行
- [✓] `examples/runbooks/0102-modify-dns-hostname.yaml` を新スキーマに移行
- [✓] 旧テンプレート削除：`templates/ec2-create-vpc.md.j2` / `templates/ec2-modify-vpc-attribute.md.j2`
- [✓] `generate.py` に `params` dict 注入と `shell_var` フィルタを追加

### 検証
- [✓] 既知課題2件の解消を確認
  - 0102 主処理 `--vpc-id ` が空 → `--vpc-id ${VPC_ID}` に修正済み
  - `RUNBOOK_TITLE` 日本語混入 → `0102-modify-dns-hostname` に修正済み
- [✓] 0101 / 0102 の生成物が SPEC §9 の構造に従うことを確認
- [✓] スニペット側の変数規約（コマンド = shell var、例示出力 = Jinja）が両 runbook で機能することを確認

### 残課題（次のタスクで扱う）
- [ ] 監査ログ用パラメータプレビューブロックの再設計（必要なら）
- [ ] `runbook.cleanup` フィールドの導入（3.99 中間リソース削除を YAML から指定可能に）
- [ ] 複数 post_check に title/description を持たせる UI（現状は snippet のみ）

---

## フェーズ1: プロトタイプ（VPC作成シナリオ）— 完了

### スニペット作成
- [x] `snippets/ec2/create-vpc.md`
- [x] `snippets/ec2/describe-vpcs.md`
- [x] `snippets/ec2/describe-vpc-attribute.md`
- [x] `snippets/ec2/modify-vpc-attribute.md`

### テンプレート作成
- [x] `templates/ec2-create-vpc.md.j2`
- [x] `templates/ec2-modify-vpc-attribute.md.j2`

### サンプルYAML作成
- [x] `examples/scenarios/0100-create-vpc.yaml`（フェーズ0で廃止予定）
- [x] `examples/runbooks/0101-create-vpc.yaml`
- [x] `examples/runbooks/0102-modify-dns-hostname.yaml`

### 生成ツール実装
- [✓] `generate.py` の基本実装（フェーズ0でCLIを刷新予定）
  - [✓] YAML読み込み（シナリオ・手順書）
  - [✓] パラメータ解決（シナリオ共通 → 手順書固有のマージ）
  - [✓] テンプレート解決（プロジェクト側 → 共通側のフォールバック）※フェーズ0で固定パスに簡素化
  - [✓] Jinja2によるMarkdown生成
  - [✓] スニペットのinclude展開

### 検証
- [✓] VPC作成シナリオのMarkdown生成（成功：`examples/dist/scenarios/0100-create-vpc.md` ほか2件を生成）
- [ ] 生成物と現行手順書（0101-CreateVPC-Runbook.md, 0102-ModifyDNSHostname-Runbook.md）の比較確認
- [ ] 生成物がCloudShellで読みながら実行できる品質であることの確認

### 既知の課題 — フェーズ1.5 で解消済み
- ~~`templates/ec2-modify-vpc-attribute.md.j2` で include する `snippets/ec2/modify-vpc-attribute.md` および `describe-vpc-attribute.md` が `{{ vpc_id }}` を要求するが、テンプレート/YAML 側でセットされていないため `--vpc-id ` の値が空になる~~ → スニペットをシェル変数規約に変更し、事前確認で取得した `${VPC_ID}` がそのまま伝播する形に解決
- ~~`templates/ec2-modify-vpc-attribute.md.j2` の `RUNBOOK_TITLE` が `runbook.title | lower | replace(' ', '-')` から生成されているため、日本語タイトルでは使い物にならない~~ → runbook YAML に `slug` フィールドを追加し、`{{ runbook.id }}-{{ runbook.slug }}` で生成する形に解決

---

## フェーズ2: SSMパラメータ対応（予定）

- [ ] `snippets/ssm/put-parameter.md`
- [ ] `snippets/ssm/describe-parameters.md`
- [ ] `templates/ssm-put-parameters.md.j2`（ループ展開対応）
- [ ] サンプルYAML作成
- [ ] 生成・検証

## フェーズ3: 追加操作タイプ（予定）

- [ ] S3: バケット作成、バージョニング設定
- [ ] KMS: キー作成
- [ ] CloudFormation: スタック操作

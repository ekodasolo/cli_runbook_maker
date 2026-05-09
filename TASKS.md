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
- [×] ~~監査ログ用パラメータプレビューブロックの再設計~~ — **不要として閉鎖**。即値レンダリング方針（フェーズ1.6）の下では runbook 自身が記録になるため監査ログは冗長
- [×] ~~`runbook.cleanup` フィールドの導入~~ — **不要として閉鎖**（フェーズ1.7）。実運用で「中間リソースの削除」が必要なケースはまず出てこないため、3.99 セクションごと撤廃
- [ ] 複数 post_check に title/description を持たせる UI（現状は snippet のみ）

---

## フェーズ1.7: 3.99 中間リソース削除セクションの撤廃 — 完了

実運用で「中間リソースの削除」が必要なケースはまず発生しないという判断に基づき、テンプレートから 3.99 セクションを撤廃。

### 実装
- [✓] `templates/runbook.md.j2` から 3.99 セクション（`runbook.cleanup` 参照含む）を削除
- [✓] SPEC §9 の構造図から 3.99 を削除
- [✓] フェーズ1.5 残課題の `runbook.cleanup` フィールド導入タスクを「不要として閉鎖」に変更

### 検証
- [✓] 0101 / 0102 を再生成し、3.99 セクションが消えること、Navigation が直前 section からの空行1つで続くことを確認

---

## フェーズ1.6: 即値レンダリング方針への転換

「runbook は生成されるものなので、コマンド内のパラメータ値は即値（リテラル）で書き出す」方針への転換。シェル変数で抽象化するのは実行時取得値（VPC_ID 等）に限定する。手書き時代の名残（FILE_PARAMETER 監査ログ、shell_vars 代入ブロック）を撤去し、画面に出ているコマンドが流したコマンドそのもの、という1対1対応を確立する。

### 設計
- [✓] スニペット規約：静的設定は Jinja2 即値、実行時取得値は `${VPC_ID}` 等のシェル変数（SPEC §6.6 で明文化）
- [✓] パラメータ値の YAML 表記規約：JSON リテラルと一致する文字列で書く（`value: "true"`、`value: "30"` 等。SPEC §6.7）
- [✓] 1.1 セクションをパラメータ表に統合。FILE_PARAMETER 設定 / shell_vars 代入 / `cat << ETX` 確認ブロックを撤去
- [✓] runbook YAML スキーマから `shell_vars` / `slug` フィールドを撤去

### 実装
- [✓] `templates/runbook.md.j2` の 1.1 セクションをパラメータ表に置き換え
- [✓] スニペット7件を即値ベースに書き換え（`create-vpc.md` / `describe-vpcs.md` / `modify-vpc-attribute.md` / `describe-vpc-attribute.md` / `list-vpcs.md` / `find-vpc-id-by-cidr.md` / `describe-vpc-dns-attributes.md`）
- [✓] `examples/runbooks/0101-create-vpc.yaml` / `0102-modify-dns-hostname.yaml` から `shell_vars` / `slug` 撤去、`value: "true"` を文字列化
- [✓] `generate.py` から不要になった `shell_var` フィルタ撤去、コメントを新仕様に合わせて修正
- [✓] SPEC §4.1（YAML スキーマ）、§6.4（テンプレートの責務）、§6.6（変数規約）、§6.7（YAML 表記規約）、§9（生成構造）、§9.1（パラメータ表）を更新

### 検証
- [✓] 0101 / 0102 の生成物が即値で出力されることを確認（`--cidr-block 10.0.0.0/24`、`--region ap-northeast-1` 等）
- [✓] 0102 の主処理コマンドで `${VPC_ID}` のみシェル変数、その他は即値で出力されることを確認
- [✓] 1.1 のパラメータ表とコマンド本体の値が一致することを確認（`value: true` の表記不一致を修正済み）
- [✓] 連続生成で MD5 一致（冪等性）

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

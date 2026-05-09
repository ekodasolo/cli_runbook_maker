# Runbook Toolkit タスクリスト

## フェーズ0: 仕様の簡素化（実施中）

3層構造（シナリオ／手順書／スニペット）から2層構造（手順書／スニペット）に変更し、ツールキット／プロジェクトのリポジトリ分離も廃止する。詳細は SPEC.md 参照。

### 仕様ドキュメントの刷新
- [✓] SPEC.md の刷新（2層構造、シングルリポジトリ、`params_files` 機構、新CLI）
- [✓] TASKS.md の刷新（本ファイル）
- [✓] LOGS.md に簡素化方針の決定を記録

### 実装の追従（次のブランチで実施）
- [ ] `generate.py` のCLI簡素化
  - [ ] 位置引数で runbook YAML を受け取り（複数可）、`--toolkit`／`--scenario` を廃止
  - [ ] テンプレート・スニペットの探索パスを `generate.py` 隣接ディレクトリに固定
  - [ ] `params_files` フィールドの読み込みとマージ順の実装
  - [ ] 出力先を `<runbook>.parent.parent/dist/runbooks/<basename>.md` に変更
- [ ] `templates/scenario.md.j2` を削除
- [ ] `examples/scenarios/` を削除（README 等で手順書一覧を案内する形に置き換え）
- [ ] 既存の `examples/scenarios/0100-create-vpc.yaml` の `params:` を `examples/params/training-common.yaml` に移設
- [ ] `examples/runbooks/*.yaml` に `params_files: [../params/training-common.yaml]` を追記
- [ ] `examples/runbooks/0101-create-vpc.yaml` に `navigation.next` を移設（現状はシナリオ側で順序が決まっているため）
- [ ] 動作検証：新CLIで `examples/runbooks/*.yaml` を生成し、`examples/dist/runbooks/*.md` が以前と同等の出力になることを確認

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

### 既知の課題（テンプレート側、generate.py 自体ではない／別タスクで扱う）
- `templates/ec2-modify-vpc-attribute.md.j2` で include する `snippets/ec2/modify-vpc-attribute.md` および `describe-vpc-attribute.md` が `{{ vpc_id }}` を要求するが、テンプレート/YAML 側でセットされていないため `--vpc-id ` の値が空になる。テンプレート側で `{% set vpc_id = "${VPC_ID}" %}` を追加するか、シェル変数として直書きする方針の決定が必要。
- `templates/ec2-modify-vpc-attribute.md.j2` の `RUNBOOK_TITLE` が `runbook.title | lower | replace(' ', '-')` から生成されているため、日本語タイトルでは使い物にならない（例: `0102-vpc属性を設定する`）。runbook YAML に `slug` フィールドを追加する等の方針決定が必要。

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

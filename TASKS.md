# Runbook Toolkit タスクリスト

## フェーズ1: プロトタイプ（VPC作成シナリオ）

### スニペット作成
- [x] `snippets/ec2/create-vpc.md`
- [x] `snippets/ec2/describe-vpcs.md`
- [x] `snippets/ec2/describe-vpc-attribute.md`
- [x] `snippets/ec2/modify-vpc-attribute.md`

### テンプレート作成
- [x] `templates/ec2-create-vpc.md.j2`
- [x] `templates/ec2-modify-vpc-attribute.md.j2`

### サンプルYAML作成
- [x] `examples/scenarios/0100-create-vpc.yaml`
- [x] `examples/runbooks/0101-create-vpc.yaml`
- [x] `examples/runbooks/0102-modify-dns-hostname.yaml`

### 生成ツール実装
- [✓] `generate.py` の基本実装
  - [✓] YAML読み込み（シナリオ・手順書）
  - [✓] パラメータ解決（シナリオ共通 → 手順書固有のマージ）
  - [✓] テンプレート解決（プロジェクト側 → 共通側のフォールバック）
  - [✓] Jinja2によるMarkdown生成
  - [✓] スニペットのinclude展開
  - 補足：シナリオMD用の `templates/scenario.md.j2` を新設、依存関係は `requirements.txt` に記載

### 検証
- [✓] VPC作成シナリオのMarkdown生成（成功：`examples/scenarios/0100-create-vpc.md` ほか2件を生成）
- [ ] 生成物と現行手順書（0101-CreateVPC-Runbook.md, 0102-ModifyDNSHostname-Runbook.md）の比較確認
- [ ] 生成物がCloudShellで読みながら実行できる品質であることの確認

### 既知の課題（テンプレート側、generate.py 自体ではない／次のタスクで扱う）
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

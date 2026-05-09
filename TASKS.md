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
- [ ] `generate.py` の基本実装
  - [ ] YAML読み込み（シナリオ・手順書）
  - [ ] パラメータ解決（シナリオ共通 → 手順書固有のマージ）
  - [ ] テンプレート解決（プロジェクト側 → 共通側のフォールバック）
  - [ ] Jinja2によるMarkdown生成
  - [ ] スニペットのinclude展開

### 検証
- [ ] VPC作成シナリオのMarkdown生成
- [ ] 生成物と現行手順書（0101-CreateVPC-Runbook.md, 0102-ModifyDNSHostname-Runbook.md）の比較確認
- [ ] 生成物がCloudShellで読みながら実行できる品質であることの確認

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

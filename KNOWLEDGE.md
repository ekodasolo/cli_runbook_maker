# KNOWLEDGE.md — ランブック開発のパターンとTIPS

新しいサービスやオペレーションのランブックを追加する際の設計判断に使う。


## 1. スニペット設計パターン

### 1.1 基本パターン（1コマンド・インライン）

最も一般的。1つの AWS CLI コマンドと説明・結果例で構成される。

```
[説明文]

```bash
aws <service> <command> \
    --option {{ param }} \
    --region {{ region }}
```

結果の例
```output
{ ... }
```
```

該当例: `create-vpc.md`, `put-parameter.md`, `put-bucket-versioning.md`

### 1.2 中立チェックパターン

存在確認系のスニペットは、**存在する場合と存在しない場合の両方の結果例を示す**。これにより CREATE の pre_check（非存在を期待）にも MODIFY の pre_check（存在を期待）にも同じスニペットを使い回せる。

```
[状態を確認する説明文（中立的な語調で書く）]

```bash
aws <service> <command> ...
```

[存在する場合の結果例]

[存在しない場合の結果例]
```

該当例: `describe-parameter.md`, `head-bucket.md`, `get-bucket-versioning.md`, `get-bucket-encryption.md`

**TIPS**: 「どちらの結果を期待するか」の案内はスニペット側に書かず、runbook YAML の `pre_checks[].description` に書く。これでスニペットの再利用性が保たれる。

### 1.3 実行時取得パターン（クエリ + シェル変数代入）

pre_check で AWS から取得した値を後続のステップで使う場合。クエリ結果をシェル変数に格納する。

```
[確認コマンド + 結果例]

[シェル変数取得コマンド]
```bash
VPC_ID=$(aws ec2 describe-vpcs \
    --filters "..." \
    --query "..." \
    --output text) && echo ${VPC_ID}
```
```

該当例: `find-vpc-id-by-cidr.md`

**TIPS**: シェル変数は「生成時に確定しない値」にのみ使う（即値原則、SPEC §6.6）。

### 1.4 `file://` パターン（構造化 JSON の外出し）

JSON ドキュメントが大きく構造が可変な場合に使用。3ステップ構成:

```
[説明文]

```bash
cat << 'EOF' > /tmp/<name>.json
{
    ...
}
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/<name>.json
```

[設定を適用する説明文]

```bash
aws <service> <command> \
    --option file:///tmp/<name>.json \
    --region {{ region }}
```
```

該当例: `put-bucket-lifecycle-configuration.md`, `put-bucket-policy.md`

**必須ルール**: ヒアドキュメント直後に `jq .` でフォーマットチェックを入れること。

**使い分け基準**:

| 条件 | 方式 |
| --- | --- |
| JSON なし、またはキーバリュー形式 | インライン（`Status=Enabled` 等） |
| JSON が小さく構造が固定 | インライン（`'{"Rules":[...]}'`） |
| JSON が大きい、または構造が可変 | `file://` パターン |


## 2. ランブック設計パターン

### 2.1 CREATE パターン

```
pre_checks:
  1. リソース数の上限確認（任意）
  2. 同名リソースの非存在確認        ← 中立チェックスニペットを使い、description で「非存在を期待」と案内
main:
  リソース作成コマンド
post_checks:
  1. 作成されたリソースの確認          ← 同じ中立チェックスニペットを使い、description で「存在を期待」と案内
```

該当例: `0101-create-vpc`, `0201-create-ssm-parameter-*`, `0301-create-s3-bucket`

### 2.2 MODIFY パターン

```
pre_checks:
  1. 対象リソースの存在確認            ← 中立チェックスニペット
  2. 現在の設定の確認（任意）          ← get 系スニペット
main:
  設定変更コマンド
post_checks:
  1. 変更後の設定確認                  ← pre_check と同じ get 系スニペット
```

該当例: `0102-modify-dns-hostname`, `0203-update-ssm-parameter-*`, `0302`〜`0306`

### 2.3 操作タイプの判定

| 操作の性質 | operation ラベル |
| --- | --- |
| 新規リソースを作成する | CREATE |
| 既存リソースの属性・設定を変更する | MODIFY |
| リソースを削除する | DELETE |
| ラベル・タグの付与もリソースの変更 | MODIFY |


## 3. スニペットの分離判断

### 3.1 同一 CLI コマンドでも別スニペットにする場合

**判断基準**: オプションやペイロードの違いで「意図する挙動」が異なる場合は分離する。

| 例 | 理由 |
| --- | --- |
| `put-parameter.md` vs `put-parameter-overwrite.md` | `--overwrite` の有無で「新規作成」と「既存上書き」の意味が変わる |
| `put-bucket-encryption-sse-s3.md` vs `put-bucket-encryption-sse-kms.md` | JSON ペイロードの構造が異なり、必要なパラメータも変わる |

### 3.2 1つのスニペットにまとめてよい場合

**判断基準**: §6.5 の例外規定に該当する「関連する一連のコマンド」。

| 例 | 理由 |
| --- | --- |
| `find-vpc-id-by-cidr.md`（クエリ + 変数代入） | 目的が一体（VPC ID の取得） |
| `put-bucket-lifecycle-configuration.md`（heredoc + jq + CLI） | 目的が一体（ライフサイクル設定の適用） |


## 4. パラメータ設計

### 4.1 params_files の分離基準

**サービスドメイン単位で分離する**。1.1 のパラメータ表に、そのランブックと無関係な値が出ないようにするため。

| ファイル | 含む値 | 利用ランブック |
| --- | --- | --- |
| `training-common.yaml` | `region`, `vpc_cidr`, `vpc_name` | 0101, 0102 |
| `training-ssm.yaml` | `region`, `parameter_namespace` | 0201〜0204 |
| `training-s3.yaml` | `region`, `bucket_name` | 0301〜0306 |

`region` のように複数ドメインで共通の値があっても、それぞれのファイルに重複して書く。パラメータ表の見栄えの方を優先する。

### 4.2 params_files vs params（runbook 固有）の使い分け

| 値の性質 | 置き場所 |
| --- | --- |
| 複数ランブックで共通（region, bucket_name 等） | `params_files` |
| そのランブックでのみ使う（kms_key_id, lifecycle_rule_id 等） | `params` |

### 4.3 例示出力のためだけに必要なパラメータ

スニペットの「結果の例」で Jinja2 変数を使っている場合、実際のコマンドには不要でも runbook YAML の `params` に値を書く必要がある。YAML 側にコメントで「例示出力用」と明記すること。

該当例: `0204-label-ssm-parameter-db-host.yaml` の `parameter_value`

### 4.4 値の記述規約

- JSON リテラルに埋め込まれる値は YAML 上で文字列として書く: `value: "true"`（`value: true` は NG）
- リスト値は YAML のリスト構文をそのまま使う: `parameter_labels: [production-2026-q2]`


## 5. 命名規則

### 5.1 スニペットファイル名

`snippets/{service}/{aws-cli-subcommand}.md` を基本とし、同一サブコマンドで挙動が分かれる場合はサフィックスを付ける。

```
snippets/
  ec2/
    create-vpc.md                        # aws ec2 create-vpc
    describe-vpcs.md                     # aws ec2 describe-vpcs
  ssm/
    put-parameter.md                     # aws ssm put-parameter（新規）
    put-parameter-overwrite.md           # aws ssm put-parameter --overwrite（更新）
  s3/
    put-bucket-encryption-sse-s3.md      # aws s3api put-bucket-encryption（SSE-S3）
    put-bucket-encryption-sse-kms.md     # aws s3api put-bucket-encryption（SSE-KMS）
```

### 5.2 ランブックファイル名

`{4桁ID}-{動詞}-{リソース概要}.yaml`

- ID のプレフィックスでサービスを分類: `01xx` = EC2, `02xx` = SSM, `03xx` = S3
- 動詞は操作の意図を明示: `create-`, `enable-`, `configure-`, `update-`, `label-`

### 5.3 パラメータ名

スニペット内で使う Jinja2 変数名は、AWS CLI のオプション名や API のフィールド名に寄せる。

```
region              ← --region
bucket_name         ← --bucket
vpc_cidr            ← --cidr-block の値
parameter_name      ← --name の値
kms_key_arn         ← KMSMasterKeyID の値（ARN なので _arn サフィックス）
vpc_endpoint_id     ← aws:sourceVpce の値
```


## 6. 新サービス追加の作業手順

1. **スニペットのリストアップ**: 必要な AWS CLI コマンドを洗い出し、上記パターン（§1）のどれに該当するか分類する
2. **中立チェックスニペットから作る**: 他のスニペットの pre/post_check で再利用される check 系を最初に作ると、後続の runbook 作成がスムーズ
3. **params ファイルを作る**: そのサービスドメインで共通の値を決める（最低限 `region` と主キー）
4. **CREATE ランブックを最初に作る**: 最もシンプルなパターンなので、スニペットの接続確認に向いている
5. **生成して確認**: `python generate.py` で生成し、以下を目視確認
   - 1.1 パラメータ表に不要な値がないか
   - コマンドの即値が正しく展開されているか
   - 結果例のJinja2変数が展開されているか
   - Navigation リンクのパスが正しいか
6. **MODIFY / DELETE ランブックを追加**: CREATE で作ったスニペットを check 系として再利用しながら拡張
7. **冪等性チェック**: 2回連続生成して MD5 一致を確認


## 7. よくある落とし穴

### 7.1 YAML の bool/int 変換

```yaml
# NG: Python で str(True) = "True" になり、JSON の "true" と不一致
value: true

# OK: 文字列として扱われ、そのまま "true" が出力される
value: "true"
```

### 7.2 スニペットの結果例にある未定義変数

スニペットの「結果の例」で `{{ parameter_value }}` 等を使っている場合、runbook 側の params にその変数が定義されていないと空文字で展開される。将来 StrictUndefined を有効にしたときにエラーになるので、今のうちからすべての変数に値を設定しておくこと。

### 7.3 Navigation の末尾処理

シーケンスの最後のランブックには `navigation` セクションを書かない。テンプレートは `{% if navigation.next %}` で条件分岐しているので、YAML から `navigation` キー自体を省略すれば Navigation セクションは出力されない。

### 7.4 file:// パターンで `cat << 'EOF'` を使う理由

`'EOF'`（シングルクォート）にすることで、ヒアドキュメント内のシェル変数展開を抑制する。Jinja2 変数は生成時に即値に展開されるため問題ないが、万が一 `$` を含む値（ARN 等）があった場合の誤展開を防ぐ。

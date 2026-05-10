# スニペットの解説と書き方

## スニペットとは

スニペットは1つの AWS CLI コマンドに対応する Markdown 断片ファイル。テンプレートから `{% include %}` で展開され、コマンド・説明文・結果例を提供する。

スニペット自身は「事前確認か主処理か事後確認か」を知らない。同じスニペットを複数の役割で使い回せるのが設計の要点。

## ファイルの配置

```
snippets/{service}/{aws-cli-subcommand}.md
```

- `{service}` は AWS サービス名（小文字）: `ec2`, `s3`, `ssm`, `kms`, `cloudformation`, `dynamodb`
- `{aws-cli-subcommand}` は AWS CLI のサブコマンド名に対応させる

同一サブコマンドで挙動が分かれる場合はサフィックスを付ける:

```
put-parameter.md                    # 新規作成
put-parameter-overwrite.md           # 既存上書き（--overwrite）
put-bucket-encryption-sse-s3.md      # SSE-S3
put-bucket-encryption-sse-kms.md     # SSE-KMS
```

## パターン別の書き方

### 基本パターン

最も一般的。1つのコマンドと結果例で構成する。

```markdown
バケットのバージョニングを有効にする。

```bash
aws s3api put-bucket-versioning \
    --bucket {{ bucket_name }} \
    --versioning-configuration Status=Enabled \
    --region {{ region }}
```

結果の例
```output
(出力なし — 正常終了すれば設定完了)
```
```

構成要素:
1. **説明文** — 何をするかを1行で。中立的な語調で書く
2. **コマンド** — ` ```bash ` ブロック内に記述。Jinja2 変数で即値展開
3. **結果例** — ` ```output ` ブロック。実行後に画面に出る内容を例示

### 中立チェックパターン

存在確認系のスニペットで使用。存在する場合と存在しない場合の両方の結果例を示す。

```markdown
DynamoDB テーブルの詳細を確認する。

```bash
aws dynamodb describe-table \
    --table-name {{ table_name }} \
    --region {{ region }}
```

テーブルが存在する場合の結果例:
```output
{
    "Table": {
        "TableName": "{{ table_name }}",
        "TableStatus": "ACTIVE",
        ...
    }
}
```

テーブルが存在しない場合の結果例:
```output
An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: ...
```
```

このパターンにより、CREATE の pre_check（非存在を期待）にも MODIFY の pre_check（存在を期待）にも同じスニペットを使い回せる。「どちらを期待するか」は runbook YAML の `pre_checks[].description` で案内する。

### `file://` パターン

JSON ドキュメントが大きい・構造が可変な場合に使用。3ステップ構成が必須:

```markdown
ポリシードキュメントを作成する。

```bash
cat << 'EOF' > /tmp/policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::{{ bucket_name }}/*",
            "Condition": {
                "Bool": { "aws:SecureTransport": "false" }
            }
        }
    ]
}
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/policy.json
```

バケットポリシーを設定する。

```bash
aws s3api put-bucket-policy \
    --bucket {{ bucket_name }} \
    --policy file:///tmp/policy.json \
    --region {{ region }}
```
```

ルール:
- ヒアドキュメントは `'EOF'`（シングルクォート）を使う。シェル変数の展開を抑制するため
- `jq .` によるフォーマットチェックは省略しない
- ファイルパスは `/tmp/` 配下に書き出す

使い分けの基準:

| 条件 | 方式 |
| --- | --- |
| JSON なし、またはキーバリュー形式 | インライン（`Status=Enabled` 等） |
| JSON が小さく構造が固定 | インライン（`'{"Rules":[...]}'`） |
| JSON が大きい、または構造が可変 | `file://` パターン |

### `file://` + Jinja2 ループパターン

CLI コマンドに渡すパラメータの数・名前がランブックごとに異なる場合。`file://` パターンと Jinja2 ループを組み合わせる。

```markdown
スタックパラメータファイルを作成する。

```bash
cat << 'EOF' > /tmp/stack-params.json
[
{% for p in stack_parameters %}
    {
        "ParameterKey": "{{ p.key }}",
        "ParameterValue": "{{ p.value | join(',') if p.value is sequence and p.value is not string else p.value }}"
    }{{ ',' if not loop.last else '' }}
{% endfor %}
]
EOF
```
```

重要な注意点:
- `loop.last` でカンマ制御する（JSON の末尾カンマはエラーになるため）
- 配列型の値には `join(',')` フィルタを適用する
- ループ変数（`stack_parameters`）が未定義の場合に備え、ループとその依存ブロック全体を `{% if stack_parameters %}` で囲む

### 非同期操作パターン

操作が非同期で完了を待つ必要がある場合。操作コマンドと `wait` コマンドを1つのスニペットにまとめる。

```markdown
テーブルを作成する。

```bash
aws dynamodb create-table \
    --table-name {{ table_name }} \
    ...
```

テーブルが ACTIVE になるまで待機する。プロンプトが返るまで待つ。

```bash
aws dynamodb wait table-exists \
    --table-name {{ table_name }} \
    --region {{ region }}
```

出力はなく正常終了すれば作成完了。
```

## 変数の書き方

### 即値原則

スニペット内のコマンドは、基本的に Jinja2 変数で即値展開する。

```bash
# OK: Jinja2 変数（静的設定）
aws s3api create-bucket \
    --bucket {{ bucket_name }} \
    --region {{ region }}

# OK: シェル変数（実行時取得値）
aws ec2 modify-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --region {{ region }}
```

| 値の種類 | 表記 | 例 |
| --- | --- | --- |
| 静的設定（YAML から確定） | `{{ variable }}` | `{{ region }}`, `{{ bucket_name }}` |
| 実行時取得（AWS から取得） | `${VARIABLE}` | `${VPC_ID}`, `${KEY_ID}` |

### 変数の命名

AWS CLI のオプション名や API のフィールド名に寄せる:

```
region              ← --region
bucket_name         ← --bucket
table_name          ← --table-name
partition_key_name  ← AttributeName
gsi_name            ← IndexName
```

### 結果例での変数

結果例（`output` ブロック）でも Jinja2 変数を使ってよい。実際のパラメータ値が結果例に反映されると、作業者が実際の出力と比較しやすくなる。

```output
{
    "TableName": "{{ table_name }}",
    "TableArn": "arn:aws:dynamodb:{{ region }}:123456789012:table/{{ table_name }}"
}
```

## 新しいスニペットを作る手順

1. AWS CLI コマンドのリファレンスを確認する
2. 上記のパターンから該当するものを選ぶ
3. `snippets/{service}/{subcommand}.md` にファイルを作成する
4. 説明文、コマンド、結果例を書く
5. 結果例は実際の AWS CLI 出力に近い形式にする（JSON のインデントは4スペース）
6. 中立チェック用のスニペットは存在/非存在の両パターンを書く
7. テスト用の runbook YAML を作成して生成し、出力を確認する

## よくある間違い

### 結果例の未定義変数

結果例で `{{ parameter_value }}` のような変数を使っている場合、runbook YAML の `params` にその変数が定義されていないと空文字になる。結果例で使う変数もすべて YAML 側で定義すること。

### `file://` パターンで jq を省略

jq チェックは必須。ヒアドキュメント内の JSON 構文エラー（カンマ漏れ等）を CLI 実行前に検出するためのセーフティネット。

### ループ変数のガード漏れ

`{% for p in stack_parameters %}` のようなループを使う場合、`stack_parameters` が未定義のケースを `{% if stack_parameters %}` でガードする。ガードがないと、パラメータなしの場合に空の JSON やオプションが出力される。ガードの範囲はループ単体ではなく、ヒアドキュメント・jq チェック・CLI オプション・結果例のセクションすべてを含める。

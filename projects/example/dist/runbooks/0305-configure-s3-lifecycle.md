# [0305] S3 バケットにライフサイクルルールを設定する

## About
S3 バケットにライフサイクルルールを設定する CLI 手順書。

本手順では、指定した日数が経過したオブジェクトを自動的に期限切れ（Expire）にする
ライフサイクルルールを設定する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. バケット project-dev-training-bucket が作成済みであること。
1. バージョニングが有効であること（0302 が完了済み）。

### After: 作業終了状況

以下が完了の条件。
1. ライフサイクルルールが設定されていること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| bucket_name | `project-dev-training-bucket` |
| lifecycle_rule_id | `expire-objects` |
| lifecycle_prefix | `` |
| lifecycle_expiration_days | `90` |

#### 1.2 対象バケットの存在確認

操作対象のバケットが存在することを確認する。出力なしで正常終了すれば期待通り。

指定バケットの存在を確認する。

```bash
aws s3api head-bucket \
    --bucket project-dev-training-bucket \
    --region ap-northeast-1
```

バケットが存在する場合、出力はなく正常終了する（終了コード 0）。

バケットが存在しない場合の結果例:
```output
An error occurred (404) when calling the HeadBucket operation: Not Found
```

#### 1.3 現在のライフサイクル設定の確認

ライフサイクルの現在の設定を確認する。未設定であれば NoSuchLifecycleConfiguration エラーが返る。

バケットのライフサイクル設定を確認する。

```bash
aws s3api get-bucket-lifecycle-configuration \
    --bucket project-dev-training-bucket \
    --region ap-northeast-1
```

ライフサイクルが設定されている場合の結果例:
```output
{
    "Rules": [
        {
            "ID": "expire-objects",
            "Filter": {
                "Prefix": ""
            },
            "Status": "Enabled",
            "Expiration": {
                "Days": 90
            }
        }
    ]
}
```

ライフサイクルが未設定の場合の結果例:
```output
An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist
```


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

ライフサイクル設定の JSON ドキュメントを作成する。

```bash
cat << 'EOF' > /tmp/lifecycle-config.json
{
    "Rules": [
        {
            "ID": "expire-objects",
            "Filter": {
                "Prefix": ""
            },
            "Status": "Enabled",
            "Expiration": {
                "Days": 90
            }
        }
    ]
}
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/lifecycle-config.json
```

ライフサイクル設定を適用する。

```bash
aws s3api put-bucket-lifecycle-configuration \
    --bucket project-dev-training-bucket \
    --lifecycle-configuration file:///tmp/lifecycle-config.json \
    --region ap-northeast-1
```

出力はなく正常終了すれば設定完了。

### 3. 後処理

#### 3.1 ライフサイクル設定の確認

ライフサイクルルールが設定されていることを確認する。

バケットのライフサイクル設定を確認する。

```bash
aws s3api get-bucket-lifecycle-configuration \
    --bucket project-dev-training-bucket \
    --region ap-northeast-1
```

ライフサイクルが設定されている場合の結果例:
```output
{
    "Rules": [
        {
            "ID": "expire-objects",
            "Filter": {
                "Prefix": ""
            },
            "Status": "Enabled",
            "Expiration": {
                "Days": 90
            }
        }
    ]
}
```

ライフサイクルが未設定の場合の結果例:
```output
An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist
```


#### Navigation

Next: [S3 バケットにバケットポリシーを設定する](./0306-configure-s3-bucket-policy.md)

# EOD

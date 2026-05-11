# [0603] DynamoDB TTL を設定する

## About
DynamoDB Time to Live (TTL) 設定の CLI 手順書。

本手順では、0601 で作成したテーブルに TTL を設定する。
ttl 属性に Unix エポック秒を格納すると、有効期限切れのアイテムが
自動的に削除される。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. テーブルが ACTIVE 状態であること。
1. TTL が未設定であること。

### After: 作業終了状況

以下が完了の条件。
1. TTL が ENABLED 状態であること。
1. TTL 属性が ttl であること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| table_name | `project-dev-training-table` |
| partition_key_name | `PK` |
| partition_key_type | `S` |
| sort_key_name | `SK` |
| sort_key_type | `S` |
| ttl_attribute_name | `ttl` |

#### 1.2 対象テーブルの存在確認

操作対象のテーブルが存在し、ACTIVE 状態であることを確認する。

DynamoDB テーブルの詳細を確認する。

```bash
aws dynamodb describe-table \
    --table-name project-dev-training-table \
    --region ap-northeast-1
```

テーブルが存在する場合の結果例:
```output
{
    "Table": {
        "TableName": "project-dev-training-table",
        "TableStatus": "ACTIVE",
        "KeySchema": [
            {
                "AttributeName": "PK",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "SK",
                "KeyType": "RANGE"
            }
        ],
        "AttributeDefinitions": [
            {
                "AttributeName": "PK",
                "AttributeType": "S"
            },
            {
                "AttributeName": "SK",
                "AttributeType": "S"
            }
        ],
        "BillingModeSummary": {
            "BillingMode": "PAY_PER_REQUEST"
        },
        "TableArn": "arn:aws:dynamodb:ap-northeast-1:123456789012:table/project-dev-training-table",
        "ItemCount": 0
    }
}
```

テーブルが存在しない場合の結果例:
```output
An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: project-dev-training-table not found
```

#### 1.3 TTL 設定の確認

TTL が無効（DISABLED）であることを確認する。

DynamoDB テーブルの TTL 設定を確認する。

```bash
aws dynamodb describe-time-to-live \
    --table-name project-dev-training-table \
    --region ap-northeast-1
```

TTL が有効な場合の結果例:
```output
{
    "TimeToLiveDescription": {
        "TimeToLiveStatus": "ENABLED",
        "AttributeName": "ttl"
    }
}
```

TTL が無効な場合の結果例:
```output
{
    "TimeToLiveDescription": {
        "TimeToLiveStatus": "DISABLED"
    }
}
```


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

DynamoDB テーブルの TTL を有効化する。

```bash
aws dynamodb update-time-to-live \
    --table-name project-dev-training-table \
    --time-to-live-specification "Enabled=true,AttributeName=ttl" \
    --region ap-northeast-1
```

結果の例
```output
{
    "TimeToLiveSpecification": {
        "Enabled": true,
        "AttributeName": "ttl"
    }
}
```

### 3. 後処理

#### 3.1 TTL 設定の確認

TimeToLiveStatus が ENABLED であること、
AttributeName が ttl であることを確認する。

DynamoDB テーブルの TTL 設定を確認する。

```bash
aws dynamodb describe-time-to-live \
    --table-name project-dev-training-table \
    --region ap-northeast-1
```

TTL が有効な場合の結果例:
```output
{
    "TimeToLiveDescription": {
        "TimeToLiveStatus": "ENABLED",
        "AttributeName": "ttl"
    }
}
```

TTL が無効な場合の結果例:
```output
{
    "TimeToLiveDescription": {
        "TimeToLiveStatus": "DISABLED"
    }
}
```


# EOD

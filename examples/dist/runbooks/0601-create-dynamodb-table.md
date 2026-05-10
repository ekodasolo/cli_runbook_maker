# [0601] DynamoDB テーブルを作成する

## About
DynamoDB テーブル作成の CLI 手順書。

本手順では、オンデマンドキャパシティモードのテーブルを作成する。
パーティションキー PK（文字列）とソートキー SK（文字列）の
複合キー構成で、Single Table Design を想定した汎用スキーマとする。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. DynamoDB テーブルの作成権限があること。
1. 同名のテーブルが存在しないこと。

### After: 作業終了状況

以下が完了の条件。
1. テーブルが ACTIVE 状態であること。
1. キースキーマが PK(HASH) + SK(RANGE) であること。


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

#### 1.2 既存テーブルの確認

リージョン内のテーブル一覧を確認する。

リージョン内の DynamoDB テーブル一覧を確認する。

```bash
aws dynamodb list-tables \
    --region ap-northeast-1
```

結果の例
```output
{
    "TableNames": [
        "project-dev-training-table",
        "another-table"
    ]
}
```

#### 1.3 同名テーブルの非存在確認

同名のテーブルが存在しないことを確認する。
ResourceNotFoundException が返れば作成可能。

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


### 2. 主処理

#### 2.1 リソースの操作 (CREATE)

DynamoDB テーブルを作成する。

```bash
aws dynamodb create-table \
    --table-name project-dev-training-table \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region ap-northeast-1
```

結果の例
```output
{
    "TableDescription": {
        "TableName": "project-dev-training-table",
        "TableStatus": "CREATING",
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
        "BillingModeSummary": {
            "BillingMode": "PAY_PER_REQUEST"
        },
        "TableArn": "arn:aws:dynamodb:ap-northeast-1:123456789012:table/project-dev-training-table"
    }
}
```

テーブルが ACTIVE になるまで待機する。プロンプトが返るまで待つ。

```bash
aws dynamodb wait table-exists \
    --table-name project-dev-training-table \
    --region ap-northeast-1
```

出力はなく正常終了すれば作成完了。

### 3. 後処理

#### 3.1 テーブル状態の確認

TableStatus が ACTIVE であること、
キースキーマが PK(HASH) + SK(RANGE) であることを確認する。

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


#### Navigation

Next: [DynamoDB GSI を追加する](./0602-create-dynamodb-gsi.md)

# EOD

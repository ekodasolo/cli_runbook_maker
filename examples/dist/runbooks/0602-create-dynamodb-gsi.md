# [0602] DynamoDB GSI を追加する

## About
DynamoDB Global Secondary Index (GSI) 追加の CLI 手順書。

本手順では、0601 で作成したテーブルに GSI を追加する。
GSI1PK（文字列）をパーティションキー、GSI1SK（文字列）を
ソートキーとし、全属性を射影する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. テーブルが ACTIVE 状態であること（0601 が完了済み）。

### After: 作業終了状況

以下が完了の条件。
1. GSI が ACTIVE 状態であること。
1. GSI のキースキーマが GSI1PK(HASH) + GSI1SK(RANGE) であること。


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
| gsi_name | `GSI1` |
| gsi_partition_key_name | `GSI1PK` |
| gsi_partition_key_type | `S` |
| gsi_sort_key_name | `GSI1SK` |
| gsi_sort_key_type | `S` |
| gsi_projection_type | `ALL` |

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


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

GSI 定義ファイルを作成する。

```bash
cat << 'EOF' > /tmp/gsi-update.json
[
    {
        "Create": {
            "IndexName": "GSI1",
            "KeySchema": [
                {
                    "AttributeName": "GSI1PK",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "GSI1SK",
                    "KeyType": "RANGE"
                }
            ],
            "Projection": {
                "ProjectionType": "ALL"
            }
        }
    }
]
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/gsi-update.json
```

テーブルに GSI を追加する。

```bash
aws dynamodb update-table \
    --table-name project-dev-training-table \
    --attribute-definitions \
        AttributeName=GSI1PK,AttributeType=S \
        AttributeName=GSI1SK,AttributeType=S \
    --global-secondary-index-updates file:///tmp/gsi-update.json \
    --region ap-northeast-1
```

結果の例
```output
{
    "TableDescription": {
        "TableName": "project-dev-training-table",
        "TableStatus": "UPDATING",
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "GSI1",
                "IndexStatus": "CREATING",
                "KeySchema": [
                    {
                        "AttributeName": "GSI1PK",
                        "KeyType": "HASH"
                    },
                    {
                        "AttributeName": "GSI1SK",
                        "KeyType": "RANGE"
                    }
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                }
            }
        ]
    }
}
```

テーブルが ACTIVE に戻るまで待機する。プロンプトが返るまで待つ。

```bash
aws dynamodb wait table-exists \
    --table-name project-dev-training-table \
    --region ap-northeast-1
```

出力はなく正常終了すれば GSI 追加完了。

### 3. 後処理

#### 3.1 テーブルと GSI の状態確認

テーブルが ACTIVE 状態であること、
GSI が ACTIVE で KeySchema が GSI1PK(HASH) + GSI1SK(RANGE) であることを確認する。

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

Next: [DynamoDB TTL を設定する](./0603-configure-dynamodb-ttl.md)

# EOD

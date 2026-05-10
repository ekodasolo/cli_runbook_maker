DynamoDB テーブルを作成する。

```bash
aws dynamodb create-table \
    --table-name {{ table_name }} \
    --attribute-definitions \
        AttributeName={{ partition_key_name }},AttributeType={{ partition_key_type }} \
        AttributeName={{ sort_key_name }},AttributeType={{ sort_key_type }} \
    --key-schema \
        AttributeName={{ partition_key_name }},KeyType=HASH \
        AttributeName={{ sort_key_name }},KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --region {{ region }}
```

結果の例
```output
{
    "TableDescription": {
        "TableName": "{{ table_name }}",
        "TableStatus": "CREATING",
        "KeySchema": [
            {
                "AttributeName": "{{ partition_key_name }}",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "{{ sort_key_name }}",
                "KeyType": "RANGE"
            }
        ],
        "BillingModeSummary": {
            "BillingMode": "PAY_PER_REQUEST"
        },
        "TableArn": "arn:aws:dynamodb:{{ region }}:123456789012:table/{{ table_name }}"
    }
}
```

テーブルが ACTIVE になるまで待機する。プロンプトが返るまで待つ。

```bash
aws dynamodb wait table-exists \
    --table-name {{ table_name }} \
    --region {{ region }}
```

出力はなく正常終了すれば作成完了。

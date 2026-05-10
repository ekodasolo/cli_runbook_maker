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
        "AttributeDefinitions": [
            {
                "AttributeName": "{{ partition_key_name }}",
                "AttributeType": "{{ partition_key_type }}"
            },
            {
                "AttributeName": "{{ sort_key_name }}",
                "AttributeType": "{{ sort_key_type }}"
            }
        ],
        "BillingModeSummary": {
            "BillingMode": "PAY_PER_REQUEST"
        },
        "TableArn": "arn:aws:dynamodb:{{ region }}:123456789012:table/{{ table_name }}",
        "ItemCount": 0
    }
}
```

テーブルが存在しない場合の結果例:
```output
An error occurred (ResourceNotFoundException) when calling the DescribeTable operation: Requested resource not found: Table: {{ table_name }} not found
```

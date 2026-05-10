DynamoDB テーブルの TTL 設定を確認する。

```bash
aws dynamodb describe-time-to-live \
    --table-name {{ table_name }} \
    --region {{ region }}
```

TTL が有効な場合の結果例:
```output
{
    "TimeToLiveDescription": {
        "TimeToLiveStatus": "ENABLED",
        "AttributeName": "{{ ttl_attribute_name }}"
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

DynamoDB テーブルの TTL を有効化する。

```bash
aws dynamodb update-time-to-live \
    --table-name {{ table_name }} \
    --time-to-live-specification "Enabled=true,AttributeName={{ ttl_attribute_name }}" \
    --region {{ region }}
```

結果の例
```output
{
    "TimeToLiveSpecification": {
        "Enabled": true,
        "AttributeName": "{{ ttl_attribute_name }}"
    }
}
```

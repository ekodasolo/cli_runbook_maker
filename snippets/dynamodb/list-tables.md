リージョン内の DynamoDB テーブル一覧を確認する。

```bash
aws dynamodb list-tables \
    --region {{ region }}
```

結果の例
```output
{
    "TableNames": [
        "{{ table_name }}",
        "another-table"
    ]
}
```

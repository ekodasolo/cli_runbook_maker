GSI 定義ファイルを作成する。

```bash
cat << 'EOF' > /tmp/gsi-update.json
[
    {
        "Create": {
            "IndexName": "{{ gsi_name }}",
            "KeySchema": [
                {
                    "AttributeName": "{{ gsi_partition_key_name }}",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "{{ gsi_sort_key_name }}",
                    "KeyType": "RANGE"
                }
            ],
            "Projection": {
                "ProjectionType": "{{ gsi_projection_type }}"
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
    --table-name {{ table_name }} \
    --attribute-definitions \
        AttributeName={{ gsi_partition_key_name }},AttributeType={{ gsi_partition_key_type }} \
        AttributeName={{ gsi_sort_key_name }},AttributeType={{ gsi_sort_key_type }} \
    --global-secondary-index-updates file:///tmp/gsi-update.json \
    --region {{ region }}
```

結果の例
```output
{
    "TableDescription": {
        "TableName": "{{ table_name }}",
        "TableStatus": "UPDATING",
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "{{ gsi_name }}",
                "IndexStatus": "CREATING",
                "KeySchema": [
                    {
                        "AttributeName": "{{ gsi_partition_key_name }}",
                        "KeyType": "HASH"
                    },
                    {
                        "AttributeName": "{{ gsi_sort_key_name }}",
                        "KeyType": "RANGE"
                    }
                ],
                "Projection": {
                    "ProjectionType": "{{ gsi_projection_type }}"
                }
            }
        ]
    }
}
```

テーブルが ACTIVE に戻るまで待機する。プロンプトが返るまで待つ。

```bash
aws dynamodb wait table-exists \
    --table-name {{ table_name }} \
    --region {{ region }}
```

出力はなく正常終了すれば GSI 追加完了。

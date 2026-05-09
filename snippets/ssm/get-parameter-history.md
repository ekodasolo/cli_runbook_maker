SSM パラメータのバージョン履歴を取得する（各バージョンに付与されたラベルが確認できる）。

```bash
aws ssm get-parameter-history \
    --name {{ parameter_name }} \
    --region {{ region }}
```

結果の例
```output
{
    "Parameters": [
        {
            "Name": "{{ parameter_name }}",
            "Type": "{{ parameter_type }}",
            "Value": "{{ parameter_value }}",
            "Version": 2,
            "LastModifiedDate": "2026-05-09T10:23:45.000000+09:00",
            "LastModifiedUser": "arn:aws:iam::010905949244:user/admin",
            "Description": "{{ parameter_description }}",
            "DataType": "text",
            "Labels": [
                "production-2026-q2"
            ]
        },
        {
            "Name": "{{ parameter_name }}",
            "Type": "{{ parameter_type }}",
            "Value": "db.example.com",
            "Version": 1,
            "LastModifiedDate": "2026-05-09T10:00:00.000000+09:00",
            "LastModifiedUser": "arn:aws:iam::010905949244:user/admin",
            "Description": "Training environment DB host",
            "DataType": "text",
            "Labels": []
        }
    ]
}
```

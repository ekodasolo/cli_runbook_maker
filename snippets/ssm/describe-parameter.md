指定名のパラメータの状態を確認する。

```bash
aws ssm describe-parameters \
    --filters "Key=Name,Values={{ parameter_name }}" \
    --region {{ region }}
```

パラメータが存在する場合の結果例:
```output
{
    "Parameters": [
        {
            "Name": "{{ parameter_name }}",
            "Type": "{{ parameter_type }}",
            "LastModifiedDate": "2026-05-09T10:23:45.000000+09:00",
            "LastModifiedUser": "arn:aws:iam::010905949244:user/admin",
            "Version": 1,
            "Tier": "Standard",
            "Policies": [],
            "DataType": "text"
        }
    ]
}
```

パラメータが存在しない場合の結果例:
```output
{
    "Parameters": []
}
```

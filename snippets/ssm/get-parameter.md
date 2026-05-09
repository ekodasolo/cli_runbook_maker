SSM パラメータの値を取得する。

```bash
aws ssm get-parameter \
    --name {{ parameter_name }} \
    --region {{ region }}
```

`Parameter.Value` が指定どおりの値であれば、期待通り。

結果の例
```output
{
    "Parameter": {
        "Name": "{{ parameter_name }}",
        "Type": "{{ parameter_type }}",
        "Value": "{{ parameter_value }}",
        "Version": 1,
        "LastModifiedDate": "2026-05-09T10:23:45.000000+09:00",
        "ARN": "arn:aws:ssm:{{ region }}:010905949244:parameter{{ parameter_name }}",
        "DataType": "text"
    }
}
```

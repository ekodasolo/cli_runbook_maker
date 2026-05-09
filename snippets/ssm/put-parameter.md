SSM パラメータを作成する。

```bash
aws ssm put-parameter \
    --name {{ parameter_name }} \
    --type {{ parameter_type }} \
    --value "{{ parameter_value }}" \
    --description "{{ parameter_description }}" \
    --region {{ region }}
```

結果の例
```output
{
    "Version": 1,
    "Tier": "Standard"
}
```

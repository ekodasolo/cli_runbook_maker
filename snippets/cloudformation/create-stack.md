S3 上のテンプレートの構文を検証する。エラーなく Parameters と Description が表示されれば OK。

```bash
aws cloudformation validate-template \
    --template-url {{ template_url }} \
    --region {{ region }}
```

結果の例
```output
{
{% if stack_parameters %}
    "Parameters": [
{% for p in stack_parameters %}
        {
            "ParameterKey": "{{ p.key }}",
            "DefaultValue": "{{ p.value | join(',') if p.value is sequence and p.value is not string else p.value }}",
            "NoEcho": false
        }{{ ',' if not loop.last else '' }}
{% endfor %}
    ],
{% endif %}
    "Description": "Training stack - S3 bucket with environment tagging"
}
```

{% if stack_parameters %}
スタックパラメータファイルを作成する。

```bash
cat << 'EOF' > /tmp/stack-params.json
[
{% for p in stack_parameters %}
    {
        "ParameterKey": "{{ p.key }}",
        "ParameterValue": "{{ p.value | join(',') if p.value is sequence and p.value is not string else p.value }}"
    }{{ ',' if not loop.last else '' }}
{% endfor %}
]
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/stack-params.json
```

{% endif %}
スタックを作成する。

```bash
aws cloudformation create-stack \
    --stack-name {{ stack_name }} \
    --template-url {{ template_url }} \
{% if stack_parameters %}
    --parameters file:///tmp/stack-params.json \
{% endif %}
    --tags Key=Name,Value={{ stack_name }} \
    --region {{ region }}
```

結果の例
```output
{
    "StackId": "arn:aws:cloudformation:{{ region }}:123456789012:stack/{{ stack_name }}/12345678-1234-1234-1234-123456789012"
}
```

スタック作成の完了を待機する。プロンプトが返るまで待つ。

```bash
aws cloudformation wait stack-create-complete \
    --stack-name {{ stack_name }} \
    --region {{ region }}
```

出力はなく正常終了すれば作成完了。

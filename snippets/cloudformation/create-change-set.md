{% if stack_parameters %}
変更するスタックパラメータファイルを作成する。

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
既存スタックに対して Change Set を作成する。現在のテンプレートを再利用し、パラメータのみ変更する。

```bash
aws cloudformation create-change-set \
    --stack-name {{ stack_name }} \
    --change-set-name {{ change_set_name }} \
    --use-previous-template \
{% if stack_parameters %}
    --parameters file:///tmp/stack-params.json \
{% endif %}
    --region {{ region }}
```

結果の例
```output
{
    "StackId": "arn:aws:cloudformation:{{ region }}:123456789012:stack/{{ stack_name }}/12345678-1234-1234-1234-123456789012",
    "Id": "arn:aws:cloudformation:{{ region }}:123456789012:changeSet/{{ change_set_name }}/87654321-4321-4321-4321-210987654321"
}
```

Change Set の作成完了を待機する。プロンプトが返るまで待つ。

```bash
aws cloudformation wait change-set-create-complete \
    --stack-name {{ stack_name }} \
    --change-set-name {{ change_set_name }} \
    --region {{ region }}
```

出力はなく正常終了すれば作成完了。

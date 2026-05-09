ライフサイクル設定の JSON ドキュメントを作成する。

```bash
cat << 'EOF' > /tmp/lifecycle-config.json
{
    "Rules": [
        {
            "ID": "{{ lifecycle_rule_id }}",
            "Filter": {
                "Prefix": "{{ lifecycle_prefix }}"
            },
            "Status": "Enabled",
            "Expiration": {
                "Days": {{ lifecycle_expiration_days }}
            }
        }
    ]
}
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/lifecycle-config.json
```

ライフサイクル設定を適用する。

```bash
aws s3api put-bucket-lifecycle-configuration \
    --bucket {{ bucket_name }} \
    --lifecycle-configuration file:///tmp/lifecycle-config.json \
    --region {{ region }}
```

出力はなく正常終了すれば設定完了。

バケットポリシーの JSON ドキュメントを作成する。

```bash
cat << 'EOF' > /tmp/bucket-policy.json
{% include bucket_policy_template %}

EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/bucket-policy.json
```

バケットポリシーを適用する。

```bash
aws s3api put-bucket-policy \
    --bucket {{ bucket_name }} \
    --policy file:///tmp/bucket-policy.json \
    --region {{ region }}
```

出力はなく正常終了すれば設定完了。

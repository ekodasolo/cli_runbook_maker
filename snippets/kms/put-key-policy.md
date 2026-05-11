キーポリシーの JSON ドキュメントを作成する。

```bash
cat << 'EOF' > /tmp/key-policy.json
{% include key_policy_template %}

EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/key-policy.json
```

キーポリシーを適用する。

```bash
aws kms put-key-policy \
    --key-id {{ key_ref }} \
    --policy-name default \
    --policy file:///tmp/key-policy.json \
    --region {{ region }}
```

出力はなく正常終了すれば設定完了。

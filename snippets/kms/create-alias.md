KMS キーにエイリアスを設定する。

```bash
aws kms create-alias \
    --alias-name alias/{{ key_alias }} \
    --target-key-id ${KEY_ID} \
    --region {{ region }}
```

出力はなく正常終了すれば設定完了。

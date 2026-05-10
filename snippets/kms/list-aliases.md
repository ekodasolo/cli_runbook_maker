KMS キーに設定されたエイリアスを確認する。

```bash
aws kms list-aliases \
    --key-id {{ key_ref }} \
    --region {{ region }}
```

エイリアスが設定されている場合の結果例:
```output
{
    "Aliases": [
        {
            "AliasName": "alias/project-dev-training-key",
            "AliasArn": "arn:aws:kms:ap-northeast-1:123456789012:alias/project-dev-training-key",
            "TargetKeyId": "12345678-1234-1234-1234-123456789012",
            "CreationDate": "2026-05-10T10:05:00+09:00",
            "LastUpdatedDate": "2026-05-10T10:05:00+09:00"
        }
    ]
}
```

エイリアスが未設定の場合の結果例:
```output
{
    "Aliases": []
}
```

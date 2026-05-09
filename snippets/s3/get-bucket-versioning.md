バケットのバージョニング設定を確認する。

```bash
aws s3api get-bucket-versioning \
    --bucket {{ bucket_name }} \
    --region {{ region }}
```

バージョニングが有効な場合の結果例:
```output
{
    "Status": "Enabled"
}
```

バージョニングが未設定の場合、出力は空になる。

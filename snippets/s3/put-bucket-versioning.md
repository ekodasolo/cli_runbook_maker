バケットのバージョニングを設定する。

```bash
aws s3api put-bucket-versioning \
    --bucket {{ bucket_name }} \
    --versioning-configuration Status={{ versioning_status }} \
    --region {{ region }}
```

出力はなく正常終了すれば設定完了。

バケットのデフォルト暗号化を SSE-S3 (AES256) に設定する。

```bash
aws s3api put-bucket-encryption \
    --bucket {{ bucket_name }} \
    --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' \
    --region {{ region }}
```

出力はなく正常終了すれば設定完了。

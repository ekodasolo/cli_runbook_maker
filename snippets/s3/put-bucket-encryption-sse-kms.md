バケットのデフォルト暗号化を SSE-KMS に設定する。

```bash
aws s3api put-bucket-encryption \
    --bucket {{ bucket_name }} \
    --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms","KMSMasterKeyID":"{{ kms_key_id }}"},"BucketKeyEnabled":true}]}' \
    --region {{ region }}
```

出力はなく正常終了すれば設定完了。

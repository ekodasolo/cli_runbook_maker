バケットのデフォルト暗号化設定を確認する。

```bash
aws s3api get-bucket-encryption \
    --bucket {{ bucket_name }} \
    --region {{ region }}
```

`SSEAlgorithm` が指定どおりであれば期待通り。

結果の例（SSE-S3 の場合）:
```output
{
    "ServerSideEncryptionConfiguration": {
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                },
                "BucketKeyEnabled": false
            }
        ]
    }
}
```

結果の例（SSE-KMS の場合）:
```output
{
    "ServerSideEncryptionConfiguration": {
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "aws:kms",
                    "KMSMasterKeyID": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
                },
                "BucketKeyEnabled": true
            }
        ]
    }
}
```

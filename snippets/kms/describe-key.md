KMS キーの詳細を確認する。

```bash
aws kms describe-key \
    --key-id {{ key_ref }} \
    --region {{ region }}
```

キーが存在する場合の結果例:
```output
{
    "KeyMetadata": {
        "AWSAccountId": "123456789012",
        "KeyId": "12345678-1234-1234-1234-123456789012",
        "Arn": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012",
        "CreationDate": "2026-05-10T10:00:00+09:00",
        "Enabled": true,
        "Description": "Project Dev training KMS key",
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeyState": "Enabled",
        "Origin": "AWS_KMS",
        "KeyManager": "CUSTOMER",
        "KeySpec": "SYMMETRIC_DEFAULT",
        "MultiRegion": false
    }
}
```

キーが存在しない場合の結果例:
```output
An error occurred (NotFoundException) when calling the DescribeKey operation: ...
```

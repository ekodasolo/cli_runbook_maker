KMS キーを作成し、KeyId をシェル変数に取得する。

```bash
KEY_ID=$(aws kms create-key \
    --description "{{ key_description }}" \
    --tags TagKey=Name,TagValue={{ key_name }} \
    --region {{ region }} \
    --query "KeyMetadata.KeyId" \
    --output text) && echo "Created Key: ${KEY_ID}"
```

結果の例
```output
Created Key: 12345678-1234-1234-1234-123456789012
```

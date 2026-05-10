KMS キーポリシーを確認する。

```bash
aws kms get-key-policy \
    --key-id {{ key_ref }} \
    --policy-name default \
    --query Policy \
    --output text \
    --region {{ region }} | jq .
```

結果の例:
```output
{
  "Version": "2012-10-17",
  "Id": "key-policy-1",
  "Statement": [
    {
      "Sid": "EnableRootAccountAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    }
  ]
}
```

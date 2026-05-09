バケットポリシーを確認する。

```bash
aws s3api get-bucket-policy \
    --bucket {{ bucket_name }} \
    --query Policy \
    --output text \
    --region {{ region }} | jq .
```

バケットポリシーが設定されている場合の結果例:
```output
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyNonTLSAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::{{ bucket_name }}/*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    },
    {
      "Sid": "DenyNonSpecifiedKMSEncryptedPut",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::{{ bucket_name }}/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption-aws-kms-key-id": "{{ kms_key_arn }}"
        }
      }
    },
    {
      "Sid": "DenyNonVPCEndpointAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::{{ bucket_name }}/*",
      "Condition": {
        "StringNotEquals": {
          "aws:sourceVpce": "{{ vpc_endpoint_id }}"
        }
      }
    },
    {
      "Sid": "DenyNonAuthorizedRoleGet",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::{{ bucket_name }}/*",
      "Condition": {
        "StringNotLike": {
          "aws:PrincipalArn": "{{ allowed_role_arn }}"
        }
      }
    }
  ]
}
```

バケットポリシーが未設定の場合の結果例:
```output
An error occurred (NoSuchBucketPolicy) when calling the GetBucketPolicy operation: The bucket policy does not exist
```

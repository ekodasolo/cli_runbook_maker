バケットポリシーの JSON ドキュメントを作成する。以下のポリシーは4つの制御を組み合わせたものである。

1. TLS を使用しない Get/Put を拒否
2. 指定 KMS キー以外で暗号化された Put を拒否
3. 指定 VPC エンドポイント以外からの Get/Put を拒否
4. 指定 IAM ロール以外からの Get を拒否

```bash
cat << 'EOF' > /tmp/bucket-policy.json
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
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/bucket-policy.json
```

バケットポリシーを適用する。

```bash
aws s3api put-bucket-policy \
    --bucket {{ bucket_name }} \
    --policy file:///tmp/bucket-policy.json \
    --region {{ region }}
```

出力はなく正常終了すれば設定完了。

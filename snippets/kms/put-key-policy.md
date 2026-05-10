キーポリシーの JSON ドキュメントを作成する。以下のポリシーは3つの権限を設定する。

1. ルートアカウントへのフルアクセス（キー管理の基盤）
2. 管理者ロールへのキー管理権限
3. 利用者ロールへの暗号化・復号権限

```bash
cat << 'EOF' > /tmp/key-policy.json
{
    "Version": "2012-10-17",
    "Id": "key-policy-1",
    "Statement": [
        {
            "Sid": "EnableRootAccountAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::{{ account_id }}:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "AllowKeyAdministration",
            "Effect": "Allow",
            "Principal": {
                "AWS": "{{ key_admin_role_arn }}"
            },
            "Action": [
                "kms:Create*",
                "kms:Describe*",
                "kms:Enable*",
                "kms:List*",
                "kms:Put*",
                "kms:Update*",
                "kms:Revoke*",
                "kms:Disable*",
                "kms:Get*",
                "kms:Delete*",
                "kms:TagResource",
                "kms:UntagResource",
                "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowKeyUsage",
            "Effect": "Allow",
            "Principal": {
                "AWS": "{{ key_usage_role_arn }}"
            },
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": "*"
        }
    ]
}
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/key-policy.json
```

キーポリシーを適用する。

```bash
aws kms put-key-policy \
    --key-id {{ key_ref }} \
    --policy-name default \
    --policy file:///tmp/key-policy.json \
    --region {{ region }}
```

出力はなく正常終了すれば設定完了。

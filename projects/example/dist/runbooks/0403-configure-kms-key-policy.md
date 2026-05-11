# [0403] KMS キーポリシーを設定する

## About
KMS キーポリシーを設定する CLI 手順書。

本手順では、以下の3つの権限を定義したキーポリシーを設定する。
1. ルートアカウントへのフルアクセス（キー管理の基盤）
2. 管理者ロールへのキー管理権限
3. 利用者ロールへの暗号化・復号権限


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. KMS キーが作成済みで、エイリアスが設定されていること（0401, 0402 が完了済み）。

### After: 作業終了状況

以下が完了の条件。
1. キーポリシーが設定されていること。
1. ルートアカウント、管理者ロール、利用者ロールの3つの Statement が含まれていること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| key_alias | `project-dev-training-key` |
| key_description | `Project Dev training KMS key` |
| key_name | `project-dev-training-key` |
| key_policy_template | `snippets/kms/policies/admin-usage.json.j2` |
| key_ref | `alias/project-dev-training-key` |
| account_id | `123456789012` |
| key_admin_role_arn | `arn:aws:iam::123456789012:role/project-dev-admin-role` |
| key_usage_role_arn | `arn:aws:iam::123456789012:role/project-dev-s3-role` |

#### 1.2 対象キーの存在確認

エイリアス経由でキーが参照可能であることを確認する。

KMS キーの詳細を確認する。

```bash
aws kms describe-key \
    --key-id alias/project-dev-training-key \
    --region ap-northeast-1
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

#### 1.3 現在のキーポリシーの確認

キーポリシーの現在の設定を確認する。

KMS キーポリシーを確認する。

```bash
aws kms get-key-policy \
    --key-id alias/project-dev-training-key \
    --policy-name default \
    --query Policy \
    --output text \
    --region ap-northeast-1 | jq .
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


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

キーポリシーの JSON ドキュメントを作成する。

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
                "AWS": "arn:aws:iam::123456789012:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "AllowKeyAdministration",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:role/project-dev-admin-role"
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
                "AWS": "arn:aws:iam::123456789012:role/project-dev-s3-role"
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
    --key-id alias/project-dev-training-key \
    --policy-name default \
    --policy file:///tmp/key-policy.json \
    --region ap-northeast-1
```

出力はなく正常終了すれば設定完了。

### 3. 後処理

#### 3.1 キーポリシーの確認

3つの Statement (EnableRootAccountAccess, AllowKeyAdministration,
AllowKeyUsage) がすべて設定されていることを確認する。

KMS キーポリシーを確認する。

```bash
aws kms get-key-policy \
    --key-id alias/project-dev-training-key \
    --policy-name default \
    --query Policy \
    --output text \
    --region ap-northeast-1 | jq .
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


# EOD

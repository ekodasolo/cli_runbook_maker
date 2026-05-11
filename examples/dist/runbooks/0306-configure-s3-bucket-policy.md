# [0306] S3 バケットにバケットポリシーを設定する

## About
S3 バケットにバケットポリシーを設定する CLI 手順書。

本手順では、以下の4つの制御を組み合わせたバケットポリシーを設定する。
1. TLS を使用しない Get/Put を拒否
2. 指定 KMS キー以外で暗号化された Put を拒否
3. 指定 VPC エンドポイント以外からの Get/Put を拒否
4. 指定 IAM ロール以外からの Get を拒否


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. バケット project-dev-training-bucket が作成済みであること。
1. 使用する KMS キーが作成済みであること（0304 で設定したキー）。
1. VPC エンドポイント (S3 Gateway) が作成済みであること。

### After: 作業終了状況

以下が完了の条件。
1. バケットポリシーが設定されていること。
1. 非 TLS 接続が拒否されること。
1. 指定 KMS キー以外の暗号化が拒否されること。
1. 指定 VPC エンドポイント以外からのアクセスが拒否されること。
1. 指定 IAM ロール以外からの Get が拒否されること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| bucket_name | `project-dev-training-bucket` |
| bucket_policy_template | `snippets/s3/policies/full-restriction.json.j2` |
| kms_key_arn | `arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012` |
| vpc_endpoint_id | `vpce-0123456789abcdef0` |
| allowed_role_arn | `arn:aws:iam::123456789012:role/project-dev-s3-read-role` |

#### 1.2 対象バケットの存在確認

操作対象のバケットが存在することを確認する。出力なしで正常終了すれば期待通り。

指定バケットの存在を確認する。

```bash
aws s3api head-bucket \
    --bucket project-dev-training-bucket \
    --region ap-northeast-1
```

バケットが存在する場合、出力はなく正常終了する（終了コード 0）。

バケットが存在しない場合の結果例:
```output
An error occurred (404) when calling the HeadBucket operation: Not Found
```

#### 1.3 現在のバケットポリシーの確認

バケットポリシーの現在の設定を確認する。未設定であれば NoSuchBucketPolicy エラーが返る。

バケットポリシーを確認する。

```bash
aws s3api get-bucket-policy \
    --bucket project-dev-training-bucket \
    --query Policy \
    --output text \
    --region ap-northeast-1 | jq .
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
      "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
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
      "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
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
      "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "aws:sourceVpce": "vpce-0123456789abcdef0"
        }
      }
    },
    {
      "Sid": "DenyNonAuthorizedRoleGet",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
      "Condition": {
        "StringNotLike": {
          "aws:PrincipalArn": "arn:aws:iam::123456789012:role/project-dev-s3-read-role"
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


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

バケットポリシーの JSON ドキュメントを作成する。

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
            "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
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
            "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
            "Condition": {
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
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
            "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
            "Condition": {
                "StringNotEquals": {
                    "aws:sourceVpce": "vpce-0123456789abcdef0"
                }
            }
        },
        {
            "Sid": "DenyNonAuthorizedRoleGet",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
            "Condition": {
                "StringNotLike": {
                    "aws:PrincipalArn": "arn:aws:iam::123456789012:role/project-dev-s3-read-role"
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
    --bucket project-dev-training-bucket \
    --policy file:///tmp/bucket-policy.json \
    --region ap-northeast-1
```

出力はなく正常終了すれば設定完了。

### 3. 後処理

#### 3.1 バケットポリシーの確認

4つの Statement (DenyNonTLSAccess, DenyNonSpecifiedKMSEncryptedPut,
DenyNonVPCEndpointAccess, DenyNonAuthorizedRoleGet) が
すべて設定されていることを確認する。

バケットポリシーを確認する。

```bash
aws s3api get-bucket-policy \
    --bucket project-dev-training-bucket \
    --query Policy \
    --output text \
    --region ap-northeast-1 | jq .
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
      "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
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
      "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
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
      "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "aws:sourceVpce": "vpce-0123456789abcdef0"
        }
      }
    },
    {
      "Sid": "DenyNonAuthorizedRoleGet",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::project-dev-training-bucket/*",
      "Condition": {
        "StringNotLike": {
          "aws:PrincipalArn": "arn:aws:iam::123456789012:role/project-dev-s3-read-role"
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


# EOD

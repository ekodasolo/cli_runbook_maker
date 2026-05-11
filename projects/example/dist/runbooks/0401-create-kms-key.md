# [0401] KMS キーを作成する

## About
KMS カスタマーマネージドキー作成の CLI 手順書。

本手順では、トレーニング用の対称暗号化キーを東京リージョンに作成する。
作成したキーの KeyId はシェル変数 KEY_ID に取得し、後続の手順で使用する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. KMS キーの作成権限があること。

### After: 作業終了状況

以下が完了の条件。
1. カスタマーマネージドキーが作成されていること。
1. Name タグが設定されていること。


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
| key_ref | `${KEY_ID}` |

#### 1.2 既存キーの確認

リージョン内の既存キーを確認する。

```bash
aws kms list-keys \
    --query "Keys[].[KeyId]" \
    --region ap-northeast-1
```

既存のキー数を確認する。

結果の例
```output
[
    [
        "12345678-1234-1234-1234-123456789012"
    ],
    [
        "87654321-4321-4321-4321-210987654321"
    ]
]
```


### 2. 主処理

#### 2.1 リソースの操作 (CREATE)

KMS キーを作成し、KeyId をシェル変数に取得する。

```bash
KEY_ID=$(aws kms create-key \
    --description "Project Dev training KMS key" \
    --tags TagKey=Name,TagValue=project-dev-training-key \
    --region ap-northeast-1 \
    --query "KeyMetadata.KeyId" \
    --output text) && echo "Created Key: ${KEY_ID}"
```

結果の例
```output
Created Key: 12345678-1234-1234-1234-123456789012
```

### 3. 後処理

#### 3.1 作成されたキーの確認

KeyState が Enabled、Description とタグが指定どおりであることを確認する。

KMS キーの詳細を確認する。

```bash
aws kms describe-key \
    --key-id ${KEY_ID} \
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


#### Navigation

Next: [KMS キーにエイリアスを設定する](./0402-create-kms-alias.md)

# EOD

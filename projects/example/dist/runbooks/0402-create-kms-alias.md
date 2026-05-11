# [0402] KMS キーにエイリアスを設定する

## About
KMS キーにエイリアスを設定する CLI 手順書。

本手順では、0401 で作成したキーに人間が読みやすいエイリアスを付与する。
エイリアス設定後は alias/project-dev-training-key でキーを参照できる。

前提: 0401 で取得した KEY_ID シェル変数が有効であること。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. KMS キーが作成済みであること（0401 が完了済み）。
1. KEY_ID シェル変数にキー ID が設定されていること。

### After: 作業終了状況

以下が完了の条件。
1. エイリアス alias/project-dev-training-key が設定されていること。


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

#### 1.2 対象キーの存在確認

操作対象のキーが存在し、Enabled 状態であることを確認する。

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


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

KMS キーにエイリアスを設定する。

```bash
aws kms create-alias \
    --alias-name alias/project-dev-training-key \
    --target-key-id ${KEY_ID} \
    --region ap-northeast-1
```

出力はなく正常終了すれば設定完了。

### 3. 後処理

#### 3.1 エイリアス設定の確認

エイリアスが作成され、対象キーに紐付いていることを確認する。

KMS キーに設定されたエイリアスを確認する。

```bash
aws kms list-aliases \
    --key-id ${KEY_ID} \
    --region ap-northeast-1
```

エイリアスが設定されている場合の結果例:
```output
{
    "Aliases": [
        {
            "AliasName": "alias/project-dev-training-key",
            "AliasArn": "arn:aws:kms:ap-northeast-1:123456789012:alias/project-dev-training-key",
            "TargetKeyId": "12345678-1234-1234-1234-123456789012",
            "CreationDate": "2026-05-10T10:05:00+09:00",
            "LastUpdatedDate": "2026-05-10T10:05:00+09:00"
        }
    ]
}
```

エイリアスが未設定の場合の結果例:
```output
{
    "Aliases": []
}
```


#### Navigation

Next: [KMS キーポリシーを設定する](./0403-configure-kms-key-policy.md)

# EOD

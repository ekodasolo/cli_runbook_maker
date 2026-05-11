# [0303] S3 バケットにデフォルト暗号化 (SSE-S3) を設定する

## About
S3 バケットのデフォルト暗号化を SSE-S3 (AES256) に設定する CLI 手順書。

本手順では、バケットに保存されるオブジェクトのデフォルト暗号化方式を
S3 マネージドキー (SSE-S3) に明示的に設定する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. バケット project-dev-training-bucket が作成済みであること。

### After: 作業終了状況

以下が完了の条件。
1. バケットのデフォルト暗号化が SSE-S3 (AES256) に設定されていること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| bucket_name | `project-dev-training-bucket` |

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

#### 1.3 現在の暗号化設定の確認

デフォルト暗号化の現在の設定を確認する。

バケットのデフォルト暗号化設定を確認する。

```bash
aws s3api get-bucket-encryption \
    --bucket project-dev-training-bucket \
    --region ap-northeast-1
```

`SSEAlgorithm` が指定どおりであれば期待通り。

結果の例（SSE-S3 の場合）:
```output
{
    "ServerSideEncryptionConfiguration": {
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                },
                "BucketKeyEnabled": false
            }
        ]
    }
}
```

結果の例（SSE-KMS の場合）:
```output
{
    "ServerSideEncryptionConfiguration": {
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "aws:kms",
                    "KMSMasterKeyID": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
                },
                "BucketKeyEnabled": true
            }
        ]
    }
}
```

デフォルト暗号化が未設定の場合の結果例:
```output
An error occurred (ServerSideEncryptionConfigurationNotFoundError) when calling the GetBucketEncryption operation: The server side encryption configuration was not found
```


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

バケットのデフォルト暗号化を SSE-S3 (AES256) に設定する。

```bash
aws s3api put-bucket-encryption \
    --bucket project-dev-training-bucket \
    --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' \
    --region ap-northeast-1
```

出力はなく正常終了すれば設定完了。

### 3. 後処理

#### 3.1 暗号化設定の確認

SSEAlgorithm が AES256 になっていることを確認する。

バケットのデフォルト暗号化設定を確認する。

```bash
aws s3api get-bucket-encryption \
    --bucket project-dev-training-bucket \
    --region ap-northeast-1
```

`SSEAlgorithm` が指定どおりであれば期待通り。

結果の例（SSE-S3 の場合）:
```output
{
    "ServerSideEncryptionConfiguration": {
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                },
                "BucketKeyEnabled": false
            }
        ]
    }
}
```

結果の例（SSE-KMS の場合）:
```output
{
    "ServerSideEncryptionConfiguration": {
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "aws:kms",
                    "KMSMasterKeyID": "arn:aws:kms:ap-northeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
                },
                "BucketKeyEnabled": true
            }
        ]
    }
}
```

デフォルト暗号化が未設定の場合の結果例:
```output
An error occurred (ServerSideEncryptionConfigurationNotFoundError) when calling the GetBucketEncryption operation: The server side encryption configuration was not found
```


#### Navigation

Next: [S3 バケットにデフォルト暗号化 (SSE-KMS) を設定する](./0304-configure-s3-encryption-sse-kms.md)

# EOD

# [0302] S3 バケットのバージョニングを有効にする

## About
S3 バケットのバージョニング設定を有効にする CLI 手順書。

本手順では、バケットのバージョニングを有効化し、オブジェクトの世代管理を可能にする。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. バケット project-dev-training-bucket が作成済みであること（0301 が完了済み）。

### After: 作業終了状況

以下が完了の条件。
1. バケットのバージョニングが Enabled になっていること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| bucket_name | `project-dev-training-bucket` |
| versioning_status | `Enabled` |

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

#### 1.3 現在のバージョニング設定の確認

バージョニングの現在の状態を確認する。

バケットのバージョニング設定を確認する。

```bash
aws s3api get-bucket-versioning \
    --bucket project-dev-training-bucket \
    --region ap-northeast-1
```

バージョニングが有効な場合の結果例:
```output
{
    "Status": "Enabled"
}
```

バージョニングが未設定の場合、出力は空になる。


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

バケットのバージョニングを設定する。

```bash
aws s3api put-bucket-versioning \
    --bucket project-dev-training-bucket \
    --versioning-configuration Status=Enabled \
    --region ap-northeast-1
```

出力はなく正常終了すれば設定完了。

### 3. 後処理

#### 3.1 バージョニング設定の確認

バージョニングが Enabled になっていることを確認する。

バケットのバージョニング設定を確認する。

```bash
aws s3api get-bucket-versioning \
    --bucket project-dev-training-bucket \
    --region ap-northeast-1
```

バージョニングが有効な場合の結果例:
```output
{
    "Status": "Enabled"
}
```

バージョニングが未設定の場合、出力は空になる。


#### Navigation

Next: [S3 バケットにデフォルト暗号化 (SSE-S3) を設定する](./0303-configure-s3-encryption-sse-s3.md)

# EOD

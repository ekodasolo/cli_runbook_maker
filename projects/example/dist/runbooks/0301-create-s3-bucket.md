# [0301] S3 バケットを作成する

## About
S3 バケット作成の CLI 手順書。

本手順では、トレーニング用の S3 バケットを東京リージョンに作成する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. 同名のバケットがまだ作成されていないこと。
1. アカウントのバケット数が上限に達していないこと。

### After: 作業終了状況

以下が完了の条件。
1. バケット project-dev-training-bucket が作成されていること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| bucket_name | `project-dev-training-bucket` |

#### 1.2 バケット数の確認

アカウント内の既存バケット数を確認する。

```bash
aws s3api list-buckets \
    --query "Buckets[].[BucketName, CreationDate]" \
    --region ap-northeast-1
```

既存のバケット数がアカウント上限に達していなければ期待通り。

結果の例
```output
[
    [
        "my-existing-bucket-1",
        "2025-01-15T03:24:18+00:00"
    ],
    [
        "my-existing-bucket-2",
        "2025-06-20T11:05:32+00:00"
    ]
]
```

#### 1.3 同名バケットの非存在確認

作成対象のバケットがまだ存在しないことを確認する。404 エラーが返れば期待通り。

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


### 2. 主処理

#### 2.1 リソースの操作 (CREATE)

S3 バケットを作成する。

```bash
aws s3api create-bucket \
    --bucket project-dev-training-bucket \
    --create-bucket-configuration LocationConstraint=ap-northeast-1 \
    --region ap-northeast-1
```

結果の例
```output
{
    "Location": "http://project-dev-training-bucket.s3.amazonaws.com/"
}
```

### 3. 後処理

#### 3.1 バケットの作成確認

バケットが正常に作成され、アクセス可能であることを確認する。出力なしで正常終了すれば期待通り。

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


#### Navigation

Next: [S3 バケットのバージョニングを有効にする](./0302-enable-s3-versioning.md)

# EOD

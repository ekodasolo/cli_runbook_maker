# [0501] CFn スタックを作成する

## About
CloudFormation スタック作成の CLI 手順書。

本手順では、S3 上のテンプレートを使用してトレーニング用スタックを
東京リージョンにデプロイする。テンプレートは S3 バケットを1つ作成し、
Environment パラメータでタグを制御する。初回は dev 環境として作成する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. CloudFormation スタックの作成権限があること。
1. テンプレートが S3 にアップロード済みであること。
1. 同名のスタックが存在しないこと。

### After: 作業終了状況

以下が完了の条件。
1. スタックが CREATE_COMPLETE 状態であること。
1. Outputs に BucketName と BucketArn が出力されていること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| stack_name | `project-dev-training-stack` |
| change_set_name | `project-dev-update-env` |
| template_url | `https://s3.ap-northeast-1.amazonaws.com/project-dev-cfn-templates/training-stack.yaml` |

stack_parameters：

| ParameterKey | ParameterValue |
| --- | --- |
| Environment | `dev` |

#### 1.2 既存スタックの確認

リージョン内のアクティブなスタックを確認する。

リージョン内のアクティブなスタック一覧を確認する。

```bash
aws cloudformation list-stacks \
    --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE UPDATE_ROLLBACK_COMPLETE \
    --query "StackSummaries[].[StackName,StackStatus,CreationTime]" \
    --output table \
    --region ap-northeast-1
```

結果の例
```output
-------------------------------------------------------------------
|                          ListStacks                             |
+------------------------------+-----------------+----------------+
|  project-dev-training-stack  | CREATE_COMPLETE | 2026-05-10T... |
|  another-stack               | UPDATE_COMPLETE | 2026-05-01T... |
+------------------------------+-----------------+----------------+
```

#### 1.3 同名スタックの非存在確認

同名のスタックが存在しないことを確認する。
ValidationError が返れば作成可能。

CloudFormation スタックの詳細を確認する。

```bash
aws cloudformation describe-stacks \
    --stack-name project-dev-training-stack \
    --region ap-northeast-1
```

スタックが存在する場合の結果例:
```output
{
    "Stacks": [
        {
            "StackName": "project-dev-training-stack",
            "StackId": "arn:aws:cloudformation:ap-northeast-1:123456789012:stack/project-dev-training-stack/12345678-1234-1234-1234-123456789012",
            "StackStatus": "CREATE_COMPLETE",
            "CreationTime": "2026-05-10T10:00:00.000000+00:00",
            "Description": "Training stack - S3 bucket with environment tagging",
            "Parameters": [
                {
                    "ParameterKey": "Environment",
                    "ParameterValue": "dev"
                }
            ],
            "Outputs": [
                {
                    "OutputKey": "BucketName",
                    "OutputValue": "project-dev-training-stack-trainingbucket-abc123"
                },
                {
                    "OutputKey": "BucketArn",
                    "OutputValue": "arn:aws:s3:::project-dev-training-stack-trainingbucket-abc123"
                }
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "project-dev-training-stack"
                }
            ]
        }
    ]
}
```

スタックが存在しない場合の結果例:
```output
An error occurred (ValidationError) when calling the DescribeStacks operation: Stack with id project-dev-training-stack does not exist
```


### 2. 主処理

#### 2.1 リソースの操作 (CREATE)

S3 上のテンプレートの構文を検証する。エラーなく Parameters と Description が表示されれば OK。

```bash
aws cloudformation validate-template \
    --template-url https://s3.ap-northeast-1.amazonaws.com/project-dev-cfn-templates/training-stack.yaml \
    --region ap-northeast-1
```

結果の例
```output
{
    "Parameters": [
        {
            "ParameterKey": "Environment",
            "DefaultValue": "dev",
            "NoEcho": false
        }
    ],
    "Description": "Training stack - S3 bucket with environment tagging"
}
```

スタックパラメータファイルを作成する。

```bash
cat << 'EOF' > /tmp/stack-params.json
[
    {
        "ParameterKey": "Environment",
        "ParameterValue": "dev"
    }
]
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/stack-params.json
```

スタックを作成する。

```bash
aws cloudformation create-stack \
    --stack-name project-dev-training-stack \
    --template-url https://s3.ap-northeast-1.amazonaws.com/project-dev-cfn-templates/training-stack.yaml \
    --parameters file:///tmp/stack-params.json \
    --tags Key=Name,Value=project-dev-training-stack \
    --region ap-northeast-1
```

結果の例
```output
{
    "StackId": "arn:aws:cloudformation:ap-northeast-1:123456789012:stack/project-dev-training-stack/12345678-1234-1234-1234-123456789012"
}
```

スタック作成の完了を待機する。プロンプトが返るまで待つ。

```bash
aws cloudformation wait stack-create-complete \
    --stack-name project-dev-training-stack \
    --region ap-northeast-1
```

出力はなく正常終了すれば作成完了。

### 3. 後処理

#### 3.1 スタック状態の確認

StackStatus が CREATE_COMPLETE であること、
Outputs に BucketName と BucketArn が出力されていることを確認する。

CloudFormation スタックの詳細を確認する。

```bash
aws cloudformation describe-stacks \
    --stack-name project-dev-training-stack \
    --region ap-northeast-1
```

スタックが存在する場合の結果例:
```output
{
    "Stacks": [
        {
            "StackName": "project-dev-training-stack",
            "StackId": "arn:aws:cloudformation:ap-northeast-1:123456789012:stack/project-dev-training-stack/12345678-1234-1234-1234-123456789012",
            "StackStatus": "CREATE_COMPLETE",
            "CreationTime": "2026-05-10T10:00:00.000000+00:00",
            "Description": "Training stack - S3 bucket with environment tagging",
            "Parameters": [
                {
                    "ParameterKey": "Environment",
                    "ParameterValue": "dev"
                }
            ],
            "Outputs": [
                {
                    "OutputKey": "BucketName",
                    "OutputValue": "project-dev-training-stack-trainingbucket-abc123"
                },
                {
                    "OutputKey": "BucketArn",
                    "OutputValue": "arn:aws:s3:::project-dev-training-stack-trainingbucket-abc123"
                }
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "project-dev-training-stack"
                }
            ]
        }
    ]
}
```

スタックが存在しない場合の結果例:
```output
An error occurred (ValidationError) when calling the DescribeStacks operation: Stack with id project-dev-training-stack does not exist
```

#### 3.2 スタックイベントの確認

すべてのリソースが CREATE_COMPLETE になっていることを確認する。

スタックの直近のイベントを確認する。

```bash
aws cloudformation describe-stack-events \
    --stack-name project-dev-training-stack \
    --query "StackEvents[:10].[Timestamp,ResourceType,LogicalResourceId,ResourceStatus]" \
    --output table \
    --region ap-northeast-1
```

結果の例
```output
---------------------------------------------------------------------------------------
|                              DescribeStackEvents                                    |
+---------------------------+--------------------+------------------+-----------------+
|  2026-05-10T10:01:00.00Z  | AWS::CloudFormation::Stack | project-dev-training-stack  | CREATE_COMPLETE |
|  2026-05-10T10:00:55.00Z  | AWS::S3::Bucket    | TrainingBucket   | CREATE_COMPLETE |
|  2026-05-10T10:00:30.00Z  | AWS::S3::Bucket    | TrainingBucket   | CREATE_IN_PROGRESS |
|  2026-05-10T10:00:10.00Z  | AWS::CloudFormation::Stack | project-dev-training-stack  | CREATE_IN_PROGRESS |
+---------------------------+--------------------+------------------+-----------------+
```

すべてのリソースが `CREATE_COMPLETE` または `UPDATE_COMPLETE` になっていれば正常。


#### Navigation

Next: [CFn Change Set を作成する](./0502-create-cfn-change-set.md)

# EOD

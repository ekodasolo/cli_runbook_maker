# [0504] CFn スタックを削除する

## About
CloudFormation スタック削除の CLI 手順書。

本手順では、トレーニング用スタックとスタック内のすべてのリソース（S3 バケット）を
削除する。削除後はスタックが存在しないことを確認する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. 削除対象のスタックが存在すること（0501 が完了済み）。
1. スタック内のリソース（S3 バケット）が空であること。

### After: 作業終了状況

以下が完了の条件。
1. スタックが削除されていること（describe-stacks で ValidationError が返ること）。


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
| Environment | `staging` |

#### 1.2 削除対象スタックの確認

削除対象のスタックが存在し、その状態を確認する。

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
                    "ParameterValue": "staging"
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

#### 2.1 リソースの操作 (DELETE)

スタックを削除する。スタック内のすべてのリソースが削除される。

```bash
aws cloudformation delete-stack \
    --stack-name project-dev-training-stack \
    --region ap-northeast-1
```

出力はなく正常終了すれば削除開始。

スタック削除の完了を待機する。プロンプトが返るまで待つ。

```bash
aws cloudformation wait stack-delete-complete \
    --stack-name project-dev-training-stack \
    --region ap-northeast-1
```

出力はなく正常終了すれば削除完了。

### 3. 後処理

#### 3.1 スタック削除の確認

スタックが削除されていることを確認する。
ValidationError（does not exist）が返れば削除完了。

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
                    "ParameterValue": "staging"
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


# EOD

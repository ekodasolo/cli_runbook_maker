# [0503] CFn Change Set を実行する

## About
CloudFormation Change Set 実行の CLI 手順書。

本手順では、0502 で作成した Change Set を実行し、スタックを更新する。
Environment パラメータが dev から staging に変更され、
S3 バケットの Environment タグが更新される。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. Change Set が CREATE_COMPLETE かつ AVAILABLE 状態であること（0502 が完了済み）。

### After: 作業終了状況

以下が完了の条件。
1. スタックが UPDATE_COMPLETE 状態であること。
1. Environment パラメータが staging に変更されていること。


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

#### 1.2 Change Set の実行可能確認

Change Set の Status が CREATE_COMPLETE、
ExecutionStatus が AVAILABLE であることを確認する。

Change Set の詳細を確認する。

```bash
aws cloudformation describe-change-set \
    --stack-name project-dev-training-stack \
    --change-set-name project-dev-update-env \
    --region ap-northeast-1
```

Change Set が存在する場合の結果例:
```output
{
    "ChangeSetName": "project-dev-update-env",
    "StackName": "project-dev-training-stack",
    "Status": "CREATE_COMPLETE",
    "ExecutionStatus": "AVAILABLE",
    "Changes": [
        {
            "Type": "Resource",
            "ResourceChange": {
                "Action": "Modify",
                "LogicalResourceId": "TrainingBucket",
                "ResourceType": "AWS::S3::Bucket",
                "Replacement": "False",
                "Details": [
                    {
                        "Target": {
                            "Attribute": "Tags",
                            "RequiresRecreation": "Never"
                        },
                        "Evaluation": "Static",
                        "ChangeSource": "ParameterReference"
                    }
                ]
            }
        }
    ],
    "Parameters": [
        {
            "ParameterKey": "Environment",
            "ParameterValue": "staging"
        }
    ]
}
```

Change Set が存在しない場合の結果例:
```output
An error occurred (ChangeSetNotFoundException) when calling the DescribeChangeSet operation: ChangeSet [project-dev-update-env] does not exist
```


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

Change Set を実行し、スタックを更新する。

```bash
aws cloudformation execute-change-set \
    --stack-name project-dev-training-stack \
    --change-set-name project-dev-update-env \
    --region ap-northeast-1
```

出力はなく正常終了すれば実行開始。

スタック更新の完了を待機する。プロンプトが返るまで待つ。

```bash
aws cloudformation wait stack-update-complete \
    --stack-name project-dev-training-stack \
    --region ap-northeast-1
```

出力はなく正常終了すれば更新完了。

### 3. 後処理

#### 3.1 スタック状態の確認

StackStatus が UPDATE_COMPLETE であること、
Parameters の Environment が staging に変更されていることを確認する。

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

#### 3.2 スタックイベントの確認

すべてのリソースが UPDATE_COMPLETE になっていることを確認する。

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

Next: [CFn スタックを削除する](./0504-delete-cfn-stack.md)

# EOD

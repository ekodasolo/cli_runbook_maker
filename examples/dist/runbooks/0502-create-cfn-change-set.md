# [0502] CFn Change Set を作成する

## About
CloudFormation Change Set 作成の CLI 手順書。

本手順では、0501 で作成したスタックに対して Change Set を作成する。
Environment パラメータを dev から staging に変更し、
変更内容をプレビューできる状態にする。

Change Set の実行（適用）は次の手順 0503 で行う。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. スタックが CREATE_COMPLETE または UPDATE_COMPLETE 状態であること（0501 が完了済み）。

### After: 作業終了状況

以下が完了の条件。
1. Change Set が CREATE_COMPLETE かつ ExecutionStatus が AVAILABLE であること。
1. Changes に TrainingBucket の Tags 変更が表示されていること。


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

#### 1.2 対象スタックの存在確認

操作対象のスタックが存在し、CREATE_COMPLETE または UPDATE_COMPLETE
状態であることを確認する。

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

#### 2.1 リソースの操作 (CREATE)

変更するスタックパラメータファイルを作成する。

```bash
cat << 'EOF' > /tmp/stack-params.json
[
    {
        "ParameterKey": "Environment",
        "ParameterValue": "staging"
    }
]
EOF
```

JSON のフォーマットを確認する。エラーなく整形結果が表示されれば OK。

```bash
jq . /tmp/stack-params.json
```

既存スタックに対して Change Set を作成する。現在のテンプレートを再利用し、パラメータのみ変更する。

```bash
aws cloudformation create-change-set \
    --stack-name project-dev-training-stack \
    --change-set-name project-dev-update-env \
    --use-previous-template \
    --parameters file:///tmp/stack-params.json \
    --region ap-northeast-1
```

結果の例
```output
{
    "StackId": "arn:aws:cloudformation:ap-northeast-1:123456789012:stack/project-dev-training-stack/12345678-1234-1234-1234-123456789012",
    "Id": "arn:aws:cloudformation:ap-northeast-1:123456789012:changeSet/project-dev-update-env/87654321-4321-4321-4321-210987654321"
}
```

Change Set の作成完了を待機する。プロンプトが返るまで待つ。

```bash
aws cloudformation wait change-set-create-complete \
    --stack-name project-dev-training-stack \
    --change-set-name project-dev-update-env \
    --region ap-northeast-1
```

出力はなく正常終了すれば作成完了。

### 3. 後処理

#### 3.1 Change Set の確認

Status が CREATE_COMPLETE、ExecutionStatus が AVAILABLE であること、
Changes に TrainingBucket の Tags 変更（Replacement: False）が
表示されていることを確認する。

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


#### Navigation

Next: [CFn Change Set を実行する](./0503-execute-cfn-change-set.md)

# EOD

スタックの直近のイベントを確認する。

```bash
aws cloudformation describe-stack-events \
    --stack-name {{ stack_name }} \
    --query "StackEvents[:10].[Timestamp,ResourceType,LogicalResourceId,ResourceStatus]" \
    --output table \
    --region {{ region }}
```

結果の例
```output
---------------------------------------------------------------------------------------
|                              DescribeStackEvents                                    |
+---------------------------+--------------------+------------------+-----------------+
|  2026-05-10T10:01:00.00Z  | AWS::CloudFormation::Stack | {{ stack_name }}  | CREATE_COMPLETE |
|  2026-05-10T10:00:55.00Z  | AWS::S3::Bucket    | TrainingBucket   | CREATE_COMPLETE |
|  2026-05-10T10:00:30.00Z  | AWS::S3::Bucket    | TrainingBucket   | CREATE_IN_PROGRESS |
|  2026-05-10T10:00:10.00Z  | AWS::CloudFormation::Stack | {{ stack_name }}  | CREATE_IN_PROGRESS |
+---------------------------+--------------------+------------------+-----------------+
```

すべてのリソースが `CREATE_COMPLETE` または `UPDATE_COMPLETE` になっていれば正常。

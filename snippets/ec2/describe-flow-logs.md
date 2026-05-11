VPC フローログの設定を確認する。

```bash
aws ec2 describe-flow-logs \
    --filters "Name=resource-id,Values=${VPC_ID}" \
    --region {{ region }}
```

フローログが設定されている場合の結果例:
```output
{
    "FlowLogs": [
        {
            "CreationTime": "2026-05-11T00:00:00.000Z",
            "FlowLogId": "fl-0a1b2c3d4e5f67890",
            "FlowLogStatus": "ACTIVE",
            "ResourceId": "vpc-0701707c27407b25d",
            "TrafficType": "ALL",
            "LogDestinationType": "s3",
            "LogDestination": "arn:aws:s3:::example-flow-logs-bucket",
            "LogFormat": "${version} ${account-id} ${interface-id} ${srcaddr} ${dstaddr} ${srcport} ${dstport} ${protocol} ${packets} ${bytes} ${start} ${end} ${action} ${log-status}",
            "MaxAggregationInterval": 600
        }
    ]
}
```

フローログが設定されていない場合の結果例:
```output
{
    "FlowLogs": []
}
```

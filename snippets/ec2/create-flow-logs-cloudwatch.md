VPC フローログを CloudWatch Logs に配信する設定を作成する。

```bash
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids ${VPC_ID} \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name {{ flow_log_log_group }} \
    --deliver-logs-permission-arn {{ flow_log_role_arn }} \
    --region {{ region }}
```

結果の例
```output
{
    "ClientToken": "abc123def456",
    "FlowLogIds": [
        "fl-0a1b2c3d4e5f67890"
    ],
    "Unsuccessful": []
}
```

`Unsuccessful` が空であれば設定完了。

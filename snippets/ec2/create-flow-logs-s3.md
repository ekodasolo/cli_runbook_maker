VPC フローログを S3 バケットに配信する設定を作成する。

```bash
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids ${VPC_ID} \
    --traffic-type ALL \
    --log-destination-type s3 \
    --log-destination {{ flow_log_s3_arn }} \
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

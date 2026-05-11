VPC にアタッチされたインターネットゲートウェイを確認する。

```bash
aws ec2 describe-internet-gateways \
    --filters "Name=attachment.vpc-id,Values=${VPC_ID}" \
    --region {{ region }}
```

インターネットゲートウェイが存在する場合の結果例:
```output
{
    "InternetGateways": [
        {
            "InternetGatewayId": "igw-0a1b2c3d4e5f67890",
            "Attachments": [
                {
                    "State": "available",
                    "VpcId": "vpc-0701707c27407b25d"
                }
            ],
            "OwnerId": "123456789012",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "{{ igw_name }}"
                }
            ]
        }
    ]
}
```

インターネットゲートウェイが存在しない場合の結果例:
```output
{
    "InternetGateways": []
}
```

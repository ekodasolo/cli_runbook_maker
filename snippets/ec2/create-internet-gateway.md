インターネットゲートウェイを作成する。

```bash
aws ec2 create-internet-gateway \
    --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value={{ igw_name }}}]" \
    --region {{ region }}
```

結果の例
```output
{
    "InternetGateway": {
        "Attachments": [],
        "InternetGatewayId": "igw-0a1b2c3d4e5f67890",
        "OwnerId": "123456789012",
        "Tags": [
            {
                "Key": "Name",
                "Value": "{{ igw_name }}"
            }
        ]
    }
}
```

インターネットゲートウェイ ID をシェル変数に取得する（後続手順で使用する）。

```bash
IGW_ID=$(aws ec2 describe-internet-gateways \
    --filters "Name=tag:Name,Values={{ igw_name }}" \
    --query "InternetGateways[0].InternetGatewayId" \
    --region {{ region }} \
    --output text) && echo ${IGW_ID}
```

出力例
```output
igw-0a1b2c3d4e5f67890
```

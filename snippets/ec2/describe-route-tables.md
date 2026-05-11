ルートテーブルの詳細を確認する。

```bash
aws ec2 describe-route-tables \
    --filters "Name=vpc-id,Values=${VPC_ID}" "Name=tag:Name,Values={{ route_table_name }}" \
    --region {{ region }}
```

ルートテーブルが存在する場合の結果例:
```output
{
    "RouteTables": [
        {
            "RouteTableId": "rtb-0a1b2c3d4e5f67890",
            "VpcId": "vpc-0701707c27407b25d",
            "Routes": [
                {
                    "DestinationCidrBlock": "{{ vpc_cidr }}",
                    "GatewayId": "local",
                    "Origin": "CreateRouteTable",
                    "State": "active"
                }
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "{{ route_table_name }}"
                }
            ],
            "Associations": [],
            "OwnerId": "123456789012"
        }
    ]
}
```

ルートテーブルが存在しない場合の結果例:
```output
{
    "RouteTables": []
}
```

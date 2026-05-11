ルートテーブルを作成する。

```bash
aws ec2 create-route-table \
    --vpc-id ${VPC_ID} \
    --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value={{ route_table_name }}}]" \
    --region {{ region }}
```

結果の例
```output
{
    "RouteTable": {
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
}
```

ルートテーブル ID をシェル変数に取得する（後続手順で使用する）。

```bash
RTB_ID=$(aws ec2 describe-route-tables \
    --filters "Name=vpc-id,Values=${VPC_ID}" "Name=tag:Name,Values={{ route_table_name }}" \
    --query "RouteTables[0].RouteTableId" \
    --region {{ region }} \
    --output text) && echo ${RTB_ID}
```

出力例
```output
rtb-0a1b2c3d4e5f67890
```

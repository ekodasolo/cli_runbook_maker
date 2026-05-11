サブネットを作成する。

```bash
aws ec2 create-subnet \
    --vpc-id ${VPC_ID} \
    --cidr-block {{ subnet_cidr }} \
    --availability-zone {{ availability_zone }} \
    --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value={{ subnet_name }}}]" \
    --region {{ region }}
```

結果の例
```output
{
    "Subnet": {
        "AvailabilityZone": "{{ availability_zone }}",
        "AvailabilityZoneId": "apne1-az4",
        "AvailableIpAddressCount": 251,
        "CidrBlock": "{{ subnet_cidr }}",
        "DefaultForAz": false,
        "MapPublicIpOnLaunch": false,
        "State": "available",
        "SubnetId": "subnet-0a1b2c3d4e5f67890",
        "VpcId": "vpc-0701707c27407b25d",
        "OwnerId": "123456789012",
        "AssignIpv6AddressOnCreation": false,
        "Tags": [
            {
                "Key": "Name",
                "Value": "{{ subnet_name }}"
            }
        ]
    }
}
```

サブネット ID をシェル変数に取得する（後続手順で使用する）。

```bash
SUBNET_ID=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=${VPC_ID}" "Name=cidr-block,Values={{ subnet_cidr }}" \
    --query "Subnets[0].SubnetId" \
    --region {{ region }} \
    --output text) && echo ${SUBNET_ID}
```

出力例
```output
subnet-0a1b2c3d4e5f67890
```

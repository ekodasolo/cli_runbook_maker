サブネットの詳細を確認する。

```bash
aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=${VPC_ID}" "Name=cidr-block,Values={{ subnet_cidr }}" \
    --region {{ region }}
```

サブネットが存在する場合の結果例:
```output
{
    "Subnets": [
        {
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
    ]
}
```

サブネットが存在しない場合の結果例:
```output
{
    "Subnets": []
}
```

VPCの一覧を確認する。

```bash
aws ec2 describe-vpcs \
    --filters "Name=cidr-block,Values={{ vpc_cidr }}" \
    --region {{ region }}
```

結果の例
```output
{
    "Vpcs": [
        {
            "CidrBlock": "{{ vpc_cidr }}",
            "DhcpOptionsId": "dopt-0ded636f18bc345d7",
            "State": "available",
            "VpcId": "vpc-0701707c27407b25d",
            "OwnerId": "010905949244",
            "InstanceTenancy": "default",
            "CidrBlockAssociationSet": [
                {
                    "AssociationId": "vpc-cidr-assoc-07a876b8ac3175c6a",
                    "CidrBlock": "{{ vpc_cidr }}",
                    "CidrBlockState": {
                        "State": "associated"
                    }
                }
            ],
            "IsDefault": false,
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "{{ vpc_name }}"
                }
            ]
        }
    ]
}
```

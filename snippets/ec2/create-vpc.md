VPCを作成する。

```bash
aws ec2 create-vpc \
    --cidr-block {{ vpc_cidr }} \
    --tag-specifications "ResourceType=vpc,Tags=[{ Key=Name,Value={{ vpc_name }} }]" \
    --region {{ region }}
```

結果の例
```output
{
    "Vpc": {
        "CidrBlock": "10.0.0.0/24",
        "DhcpOptionsId": "dopt-0ded636f18bc345d7",
        "State": "pending",
        "VpcId": "vpc-0701707c27407b25d",
        "OwnerId": "010905949244",
        "InstanceTenancy": "default",
        "Ipv6CidrBlockAssociationSet": [],
        "CidrBlockAssociationSet": [
            {
                "AssociationId": "vpc-cidr-assoc-07a876b8ac3175c6a",
                "CidrBlock": "10.0.0.0/24",
                "CidrBlockState": {
                    "State": "associated"
                }
            }
        ],
        "IsDefault": false,
        "Tags": [
            {
                "Key": "Name",
                "Value": "project-dev-main-vpc"
            }
        ]
    }
}
```

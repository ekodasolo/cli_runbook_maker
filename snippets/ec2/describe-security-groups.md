セキュリティグループの詳細を確認する。

```bash
aws ec2 describe-security-groups \
    --filters "Name=vpc-id,Values=${VPC_ID}" "Name=group-name,Values={{ security_group_name }}" \
    --region {{ region }}
```

セキュリティグループが存在する場合の結果例:
```output
{
    "SecurityGroups": [
        {
            "GroupId": "sg-0a1b2c3d4e5f67890",
            "GroupName": "{{ security_group_name }}",
            "Description": "{{ security_group_description }}",
            "VpcId": "vpc-0701707c27407b25d",
            "OwnerId": "123456789012",
            "IpPermissions": [],
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "UserIdGroupPairs": []
                }
            ],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "{{ security_group_name }}"
                }
            ]
        }
    ]
}
```

セキュリティグループが存在しない場合の結果例:
```output
{
    "SecurityGroups": []
}
```

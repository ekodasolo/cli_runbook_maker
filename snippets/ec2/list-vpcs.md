```bash
# 既存のVPCを確認
aws ec2 describe-vpcs --region ${AWS_REGION} --query "Vpcs[].[VpcId, CidrBlock]"
```

既存のVPCの数がすでに上限に達していなければ期待通り。

結果の例
```output
[
    [
        "30.1.0.0/16",
        "vpc-0e9801d129EXAMPLE",
    ],
    [
        "10.0.0.0/16",
        "vpc-06e4ab6c6cEXAMPLE",
    ]
]
```

VPCの属性値を確認する。

```bash
aws ec2 describe-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --attribute ${ATTRIBUTE} \
    --region ${AWS_REGION}
```

結果の例
```output
{
    "VpcId": "vpc-0701707c27407b25d",
    "EnableDnsHostnames": {
        "Value": true
    }
}
```

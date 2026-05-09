DNS関連のVPC属性値を確認する。

```bash
# DNS Support
aws ec2 describe-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --attribute enableDnsSupport

# DNS Hostname
aws ec2 describe-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --attribute enableDnsHostnames
```

結果の例
```output
{
    "VpcId": "vpc-0701707c27407b25d",
    "EnableDnsSupport": {
        "Value": true
    }
}
```
```output
{
    "VpcId": "vpc-0701707c27407b25d",
    "EnableDnsHostnames": {
        "Value": false
    }
}
```

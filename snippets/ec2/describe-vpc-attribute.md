VPCの属性値を確認する。

```bash
aws ec2 describe-vpc-attribute \
    --vpc-id {{ vpc_id }} \
    --attribute {{ attribute }}
```

結果の例（enableDnsHostnamesの場合）
```output
{
    "VpcId": "vpc-0701707c27407b25d",
    "EnableDnsHostnames": {
        "Value": true
    }
}
```

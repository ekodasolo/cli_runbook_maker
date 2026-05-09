VPCの属性値を変更する。

```bash
aws ec2 modify-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --{{ cli_option }} "{\"Value\":{{ value }}}" \
    --region {{ region }}
```

結果の例
```output
(出力無し)
```

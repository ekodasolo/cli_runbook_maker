VPCの属性値を変更する。

```bash
aws ec2 modify-vpc-attribute \
    --vpc-id {{ vpc_id }} \
    --{{ cli_option }} "{\"Value\":{{ value | lower }}}"
```

結果の例
```output
(出力無し)
```

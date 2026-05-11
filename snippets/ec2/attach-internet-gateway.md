インターネットゲートウェイを VPC にアタッチする。

```bash
aws ec2 attach-internet-gateway \
    --internet-gateway-id ${IGW_ID} \
    --vpc-id ${VPC_ID} \
    --region {{ region }}
```

結果の例
```output
(出力なし — 正常終了すればアタッチ完了)
```

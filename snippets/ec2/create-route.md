ルートテーブルにルートを追加する。

```bash
aws ec2 create-route \
    --route-table-id ${RTB_ID} \
    --destination-cidr-block {{ route_destination_cidr }} \
    --gateway-id ${IGW_ID} \
    --region {{ region }}
```

結果の例
```output
{
    "Return": true
}
```

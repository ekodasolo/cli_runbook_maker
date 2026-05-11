ルートテーブルをサブネットに関連付ける。

```bash
aws ec2 associate-route-table \
    --route-table-id ${RTB_ID} \
    --subnet-id ${SUBNET_ID} \
    --region {{ region }}
```

結果の例
```output
{
    "AssociationId": "rtbassoc-0a1b2c3d4e5f67890",
    "AssociationState": {
        "State": "associated"
    }
}
```

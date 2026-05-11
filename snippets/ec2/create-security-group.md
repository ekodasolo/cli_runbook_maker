セキュリティグループを作成する。

```bash
aws ec2 create-security-group \
    --group-name {{ security_group_name }} \
    --description "{{ security_group_description }}" \
    --vpc-id ${VPC_ID} \
    --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value={{ security_group_name }}}]" \
    --region {{ region }}
```

結果の例
```output
{
    "GroupId": "sg-0a1b2c3d4e5f67890"
}
```

セキュリティグループ ID をシェル変数に取得する（後続手順で使用する）。

```bash
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=vpc-id,Values=${VPC_ID}" "Name=group-name,Values={{ security_group_name }}" \
    --query "SecurityGroups[0].GroupId" \
    --region {{ region }} \
    --output text) && echo ${SG_ID}
```

出力例
```output
sg-0a1b2c3d4e5f67890
```

S3 バケットを作成する。

```bash
aws s3api create-bucket \
    --bucket {{ bucket_name }} \
    --create-bucket-configuration LocationConstraint={{ region }} \
    --region {{ region }}
```

結果の例
```output
{
    "Location": "http://{{ bucket_name }}.s3.amazonaws.com/"
}
```

バケットのライフサイクル設定を確認する。

```bash
aws s3api get-bucket-lifecycle-configuration \
    --bucket {{ bucket_name }} \
    --region {{ region }}
```

ライフサイクルが設定されている場合の結果例:
```output
{
    "Rules": [
        {
            "ID": "expire-objects",
            "Filter": {
                "Prefix": ""
            },
            "Status": "Enabled",
            "Expiration": {
                "Days": 90
            }
        }
    ]
}
```

ライフサイクルが未設定の場合の結果例:
```output
An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist
```

```bash
aws s3api list-buckets \
    --query "Buckets[].[BucketName, CreationDate]" \
    --region {{ region }}
```

既存のバケット数がアカウント上限に達していなければ期待通り。

結果の例
```output
[
    [
        "my-existing-bucket-1",
        "2025-01-15T03:24:18+00:00"
    ],
    [
        "my-existing-bucket-2",
        "2025-06-20T11:05:32+00:00"
    ]
]
```

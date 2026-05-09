指定バケットの存在を確認する。

```bash
aws s3api head-bucket \
    --bucket {{ bucket_name }} \
    --region {{ region }}
```

バケットが存在する場合、出力はなく正常終了する（終了コード 0）。

バケットが存在しない場合の結果例:
```output
An error occurred (404) when calling the HeadBucket operation: Not Found
```

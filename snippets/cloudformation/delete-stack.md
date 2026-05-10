スタックを削除する。スタック内のすべてのリソースが削除される。

```bash
aws cloudformation delete-stack \
    --stack-name {{ stack_name }} \
    --region {{ region }}
```

出力はなく正常終了すれば削除開始。

スタック削除の完了を待機する。プロンプトが返るまで待つ。

```bash
aws cloudformation wait stack-delete-complete \
    --stack-name {{ stack_name }} \
    --region {{ region }}
```

出力はなく正常終了すれば削除完了。

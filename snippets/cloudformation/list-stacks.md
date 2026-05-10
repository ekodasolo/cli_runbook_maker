リージョン内のアクティブなスタック一覧を確認する。

```bash
aws cloudformation list-stacks \
    --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE UPDATE_ROLLBACK_COMPLETE \
    --query "StackSummaries[].[StackName,StackStatus,CreationTime]" \
    --output table \
    --region {{ region }}
```

結果の例
```output
-------------------------------------------------------------------
|                          ListStacks                             |
+------------------------------+-----------------+----------------+
|  project-dev-training-stack  | CREATE_COMPLETE | 2026-05-10T... |
|  another-stack               | UPDATE_COMPLETE | 2026-05-01T... |
+------------------------------+-----------------+----------------+
```

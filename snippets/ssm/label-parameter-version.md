SSM パラメータの最新バージョンにラベルを付与する。

```bash
aws ssm label-parameter-version \
    --name {{ parameter_name }} \
    --labels {{ parameter_labels | join(' ') }} \
    --region {{ region }}
```

`InvalidLabels` が空配列であれば、すべてのラベルが正常に付与された（期待通り）。`ParameterVersion` は付与対象のバージョン番号。

結果の例
```output
{
    "InvalidLabels": [],
    "ParameterVersion": 2
}
```

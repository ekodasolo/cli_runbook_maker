指定パラメータがまだ存在していないか確認する。

```bash
aws ssm describe-parameters \
    --filters "Key=Name,Values={{ parameter_name }}" \
    --region {{ region }}
```

`Parameters` が空配列なら、まだ作成されていない（期待通り）。

結果の例
```output
{
    "Parameters": []
}
```

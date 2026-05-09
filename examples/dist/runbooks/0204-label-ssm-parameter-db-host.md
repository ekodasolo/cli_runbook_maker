# [0204] SSM パラメータ /myapp/training/db/host にラベルを付与する

## About
SSM パラメータラベル付与のCLI手順書。

本手順では、SSM Parameter Store に登録済みパラメータの最新バージョンにラベルを付与する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. パラメータ /myapp/training/db/host が作成済みであること（0201 / 0203 のいずれかが完了済み）。

### After: 作業終了状況

以下が完了の条件。
1. パラメータ /myapp/training/db/host の最新バージョンに、指定ラベルが付与されていること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| parameter_namespace | `/myapp/training/` |
| parameter_name | `/myapp/training/db/host` |
| parameter_type | `String` |
| parameter_value | `db.example.internal` |
| parameter_description | `Training environment DB host (updated for internal access)` |
| parameter_labels | `['production-2026-q2']` |

#### 1.2 対象パラメータの存在確認

指定パラメータが既に作成されていることを確認する。

指定名のパラメータの状態を確認する。

```bash
aws ssm describe-parameters \
    --filters "Key=Name,Values=/myapp/training/db/host" \
    --region ap-northeast-1
```

パラメータが存在する場合の結果例:
```output
{
    "Parameters": [
        {
            "Name": "/myapp/training/db/host",
            "Type": "String",
            "LastModifiedDate": "2026-05-09T10:23:45.000000+09:00",
            "LastModifiedUser": "arn:aws:iam::010905949244:user/admin",
            "Version": 1,
            "Tier": "Standard",
            "Policies": [],
            "DataType": "text"
        }
    ]
}
```

パラメータが存在しない場合の結果例:
```output
{
    "Parameters": []
}
```


### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

SSM パラメータの最新バージョンにラベルを付与する。

```bash
aws ssm label-parameter-version \
    --name /myapp/training/db/host \
    --labels production-2026-q2 \
    --region ap-northeast-1
```

`InvalidLabels` が空配列であれば、すべてのラベルが正常に付与された（期待通り）。`ParameterVersion` は付与対象のバージョン番号。

結果の例
```output
{
    "InvalidLabels": [],
    "ParameterVersion": 2
}
```

### 3. 後処理

#### 3.1 ラベル付与の確認

パラメータの最新バージョンに、指定ラベルが付与されていることを確認する。

SSM パラメータのバージョン履歴を取得する（各バージョンに付与されたラベルが確認できる）。

```bash
aws ssm get-parameter-history \
    --name /myapp/training/db/host \
    --region ap-northeast-1
```

結果の例
```output
{
    "Parameters": [
        {
            "Name": "/myapp/training/db/host",
            "Type": "String",
            "Value": "db.example.internal",
            "Version": 2,
            "LastModifiedDate": "2026-05-09T10:23:45.000000+09:00",
            "LastModifiedUser": "arn:aws:iam::010905949244:user/admin",
            "Description": "Training environment DB host (updated for internal access)",
            "DataType": "text",
            "Labels": [
                "production-2026-q2"
            ]
        },
        {
            "Name": "/myapp/training/db/host",
            "Type": "String",
            "Value": "db.example.com",
            "Version": 1,
            "LastModifiedDate": "2026-05-09T10:00:00.000000+09:00",
            "LastModifiedUser": "arn:aws:iam::010905949244:user/admin",
            "Description": "Training environment DB host",
            "DataType": "text",
            "Labels": []
        }
    ]
}
```


# EOD

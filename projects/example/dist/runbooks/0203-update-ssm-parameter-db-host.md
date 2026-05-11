# [0203] SSM パラメータ /myapp/training/db/host を更新する

## About
SSM パラメータ更新のCLI手順書。

本手順では、SSM Parameter Store に登録済みのパラメータの値を更新する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. パラメータ /myapp/training/db/host が作成済みであること（0201 が完了済み）。

### After: 作業終了状況

以下が完了の条件。
1. パラメータ /myapp/training/db/host の値が指定どおりに更新されていること。
1. パラメータの Version が 2 以上に増えていること。


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

#### 1.2 対象パラメータの存在確認

指定パラメータが既に作成されていることを確認する（更新対象として存在することを確認）。

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

SSM パラメータを上書きする（既存値を更新する）。

```bash
aws ssm put-parameter \
    --name /myapp/training/db/host \
    --type String \
    --value "db.example.internal" \
    --description "Training environment DB host (updated for internal access)" \
    --overwrite \
    --region ap-northeast-1
```

更新が成功すると、`Version` がインクリメントされた値で返る。

結果の例
```output
{
    "Version": 2,
    "Tier": "Standard"
}
```

### 3. 後処理

#### 3.1 更新後の値の確認

パラメータの値が指定どおりに更新されていることを確認する。

SSM パラメータの値を取得する。

```bash
aws ssm get-parameter \
    --name /myapp/training/db/host \
    --region ap-northeast-1
```

`Parameter.Value` が指定どおりの値であれば、期待通り。

結果の例
```output
{
    "Parameter": {
        "Name": "/myapp/training/db/host",
        "Type": "String",
        "Value": "db.example.internal",
        "Version": 1,
        "LastModifiedDate": "2026-05-09T10:23:45.000000+09:00",
        "ARN": "arn:aws:ssm:ap-northeast-1:010905949244:parameter/myapp/training/db/host",
        "DataType": "text"
    }
}
```


#### Navigation

Next: [SSM パラメータ /myapp/training/db/host にラベルを付与する](./0204-label-ssm-parameter-db-host.md)

# EOD

# [0202] SSM パラメータ /myapp/training/db/port を作成する

## About
SSM パラメータ作成のCLI手順書。

本手順では、SSM Parameter Store にトレーニング用 DB ポート番号のパラメータを登録する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. 同名のパラメータがまだ作成されていないこと。

### After: 作業終了状況

以下が完了の条件。
1. パラメータ /myapp/training/db/port が作成されていること。
1. 値が指定どおりに設定されていること。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータ

本手順で使うパラメータ：

| キー | 値 |
| --- | --- |
| region | `ap-northeast-1` |
| parameter_namespace | `/myapp/training/` |
| parameter_name | `/myapp/training/db/port` |
| parameter_type | `String` |
| parameter_value | `5432` |
| parameter_description | `Training environment DB port` |

#### 1.2 既存パラメータの非存在確認

指定パラメータがまだ作成されていないことを確認する。

指定名のパラメータの状態を確認する。

```bash
aws ssm describe-parameters \
    --filters "Key=Name,Values=/myapp/training/db/port" \
    --region ap-northeast-1
```

パラメータが存在する場合の結果例:
```output
{
    "Parameters": [
        {
            "Name": "/myapp/training/db/port",
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

#### 2.1 リソースの操作 (CREATE)

SSM パラメータを作成する。

```bash
aws ssm put-parameter \
    --name /myapp/training/db/port \
    --type String \
    --value "5432" \
    --description "Training environment DB port" \
    --region ap-northeast-1
```

結果の例
```output
{
    "Version": 1,
    "Tier": "Standard"
}
```

### 3. 後処理

#### 3.1 作成パラメータの値確認

パラメータが作成され、値が指定どおりに設定されていることを確認する。

SSM パラメータの値を取得する。

```bash
aws ssm get-parameter \
    --name /myapp/training/db/port \
    --region ap-northeast-1
```

`Parameter.Value` が指定どおりの値であれば、期待通り。

結果の例
```output
{
    "Parameter": {
        "Name": "/myapp/training/db/port",
        "Type": "String",
        "Value": "5432",
        "Version": 1,
        "LastModifiedDate": "2026-05-09T10:23:45.000000+09:00",
        "ARN": "arn:aws:ssm:ap-northeast-1:010905949244:parameter/myapp/training/db/port",
        "DataType": "text"
    }
}
```


#### Navigation

Next: [SSM パラメータ /myapp/training/db/host を更新する](./0203-update-ssm-parameter-db-host.md)

# EOD

# [0201] SSM パラメータ /myapp/training/db/host を作成する

## About
SSM パラメータ作成のCLI手順書。

本手順では、SSM Parameter Store にトレーニング用 DB ホスト名のパラメータを登録する。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. 同名のパラメータがまだ作成されていないこと。

### After: 作業終了状況

以下が完了の条件。
1. パラメータ /myapp/training/db/host が作成されていること。
1. 値が指定どおりに設定されていること。


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
| parameter_value | `db.example.com` |
| parameter_description | `Training environment DB host` |

#### 1.2 既存パラメータの非存在確認

指定パラメータがまだ作成されていないことを確認する。

指定パラメータがまだ存在していないか確認する。

```bash
aws ssm describe-parameters \
    --filters "Key=Name,Values=/myapp/training/db/host" \
    --region ap-northeast-1
```

`Parameters` が空配列なら、まだ作成されていない（期待通り）。

結果の例
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
    --name /myapp/training/db/host \
    --type String \
    --value "db.example.com" \
    --description "Training environment DB host" \
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
        "Value": "db.example.com",
        "Version": 1,
        "LastModifiedDate": "2026-05-09T10:23:45.000000+09:00",
        "ARN": "arn:aws:ssm:ap-northeast-1:010905949244:parameter/myapp/training/db/host",
        "DataType": "text"
    }
}
```


#### Navigation

Next: [SSM パラメータ /myapp/training/db/port を作成する](./0202-create-ssm-parameter-db-port.md)

# EOD

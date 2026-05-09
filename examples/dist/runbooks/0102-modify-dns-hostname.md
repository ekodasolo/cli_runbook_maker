# [0102] VPC属性を設定する

## About
VPCを作成するCLI手順書。

本手順では、VPCの属性値を変更し、DNS Hostnameを有効にする。


## When: 作業の条件

### Before: 事前前提条件

以下を作業の前提条件とする。
1. VPCが作成済みである。
1. VPCの属性値DNS hostnameがDisabledになっている。

### After: 作業終了状況

以下が完了の条件。
1. VPCのDNS hostnamesが、Enabledになっている。


## How: 以下は作業手順

### 1. 前処理

#### 1.1 処理パラメータの準備

パラメータの事後確認用ファイルの設定

```bash
RUNBOOK_TITLE="0102-vpc属性を設定する"
DIR_PARAMETER="."
FILE_PARAMETER="${DIR_PARAMETER}/$(date +%Y-%m-%d)-${RUNBOOK_TITLE}.env" \
    && echo ${FILE_PARAMETER}
```

手順の実行パラメータ
```bash
# 変数に値をセット
AWS_REGION="ap-northeast-1"
VPC_CIDR="10.0.0.0/24"
```

```bash
# 値を確認
cat << ETX
    AWS_REGION=${AWS_REGION}
    VPC_CIDR=${VPC_CIDR}

ETX
```


#### 1.2 事前条件1の確認

VPCが作成済みか、事前に確認する。

```bash
# 既存のVPCを確認
aws ec2 describe-vpcs --filters "Name=cidr,Values=${VPC_CIDR}"
```

VPCが作成済みであれば、期待通り。

結果の例
```output
{
    "Vpcs": [
        {
            "CidrBlock": "10.0.0.0/24",
            "DhcpOptionsId": "dopt-19edf471",
            "State": "available",
            "VpcId": "vpc-0e9801d129EXAMPLE",
            "OwnerId": "111122223333",
            "InstanceTenancy": "default",
            "CidrBlockAssociationSet": [
                {
                    "AssociationId": "vpc-cidr-assoc-062c64cfafEXAMPLE",
                    "CidrBlock": "10.0.0.0/24",
                    "CidrBlockState": {
                        "State": "associated"
                    }
                }
            ],
            "IsDefault": false
        }
    ]
}
```

VPCが作成済みならば、VPC IDを取得しておく。

```bash
VPC_ID=$(aws ec2 describe-vpcs \
    --filters "Name=cidr,Values=${VPC_CIDR}" \
    --query "Vpcs[].VpcId" \
    --region ${AWS_REGION} \
    --output text) && echo ${VPC_ID}
```

出力例
```output
vpc-0a60eb65b4EXAMPLE
```


#### 1.3 事前条件2の確認

VPCの属性値DNS hostnameがDisabledになっている。

```bash
# DNS Support
aws ec2 describe-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --attribute enableDnsSupport

# DNS Hostname
aws ec2 describe-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --attribute enableDnsHostnames
```

結果の例
```output
{
    "VpcId": "vpc-0701707c27407b25d",
    "EnableDnsSupport": {
        "Value": true
    }
}
```
```output
{
    "VpcId": "vpc-0701707c27407b25d",
    "EnableDnsHostnames": {
        "Value": false
    }
}
```

### 2. 主処理

#### 2.1 リソースの操作 (MODIFY)

パラメータの最終確認

```bash
cat << EOF > ${FILE_PARAMETER}
aws ec2 modify-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --enable-dns-hostnames "{\"Value\":true}"
        
EOF
cat ${FILE_PARAMETER}
```

処理の実行

VPCの属性値を変更する。

```bash
aws ec2 modify-vpc-attribute \
    --vpc-id  \
    --enable-dns-hostnames "{\"Value\":true}"
```

結果の例
```output
(出力無し)
```

### 3. 後処理

#### 3.1 完了条件1の結果確認
1. VPCのDNS hostnamesが、Enabledになっている。

VPCの属性値を確認する。

```bash
aws ec2 describe-vpc-attribute \
    --vpc-id  \
    --attribute enableDnsHostnames
```

結果の例（enableDnsHostnamesの場合）
```output
{
    "VpcId": "vpc-0701707c27407b25d",
    "EnableDnsHostnames": {
        "Value": true
    }
}
```


#### 3.99 中間リソースの削除

今回は特になし

#### Navigation

Next: [Subnetを作成する](./0200-CreateSubnet-Scenario.md)

# EOD

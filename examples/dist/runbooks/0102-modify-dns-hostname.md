# [0102] VPC属性を設定する

## About
VPC属性を変更するCLI手順書。

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
RUNBOOK_TITLE="0102-modify-dns-hostname"
DIR_PARAMETER="."
FILE_PARAMETER="${DIR_PARAMETER}/$(date +%Y-%m-%d)-${RUNBOOK_TITLE}.env" \
    && echo ${FILE_PARAMETER}
```

手順の実行パラメータ
```bash
# 変数に値をセット
AWS_REGION="ap-northeast-1"
VPC_CIDR="10.0.0.0/24"
ATTRIBUTE="enableDnsHostnames"
CLI_OPTION="enable-dns-hostnames"
VALUE="true"
```

```bash
# 値を確認
cat << ETX
    AWS_REGION=${AWS_REGION}
    VPC_CIDR=${VPC_CIDR}
    ATTRIBUTE=${ATTRIBUTE}
    CLI_OPTION=${CLI_OPTION}
    VALUE=${VALUE}

ETX
```

#### 1.2 VPCが作成済みであることの確認

VPCが作成済みか、事前に確認する。作成済みの場合は VPC ID を取得しておく。

```bash
# 既存のVPCを確認
aws ec2 describe-vpcs --filters "Name=cidr,Values=${VPC_CIDR}" --region ${AWS_REGION}
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

VPCが作成済みならば、VPC IDをシェル変数として取得しておく（後続手順で使用する）。

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

#### 1.3 VPC属性 (DNS Hostname) の現状確認

VPCのDNS関連属性の現状を確認する。DNS HostnameがDisabledであることを確認する。

DNS関連のVPC属性値を確認する。

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

VPCの属性値を変更する。

```bash
aws ec2 modify-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --${CLI_OPTION} "{\"Value\":${VALUE}}" \
    --region ${AWS_REGION}
```

結果の例
```output
(出力無し)
```

### 3. 後処理

#### 3.1 完了条件の結果確認

VPCのDNS hostnamesが、Enabledになっている。

VPCの属性値を確認する。

```bash
aws ec2 describe-vpc-attribute \
    --vpc-id ${VPC_ID} \
    --attribute ${ATTRIBUTE} \
    --region ${AWS_REGION}
```

結果の例
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

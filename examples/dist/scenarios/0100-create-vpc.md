# [0100] Training用VPCの作成

## About

基本的なVPC構成によるネットワークを構築する。
本シナリオでは、VPCを作成する。


## 対象リソース

- **project-dev-main-vpc** — VPC（構築するVPC）

## Who: 前提スキル

- Unixシェルの基本操作ができること
- TCP/IPの基本的な内容を理解しアドレス割り当てやIPルーティングが設定できること
- AWS CLIの基本操作ができること
- EC2/VPCへのアクセス権があること

## Where: 作業環境

CloudShellに接続し、CloudShell上で作業することを前提とする。
必要な権限をもったIAM User/IAM RoleでCloudShellを立ち上げる。


## 共通パラメータ

- `region`: `ap-northeast-1`
- `vpc_cidr`: `10.0.0.0/24`
- `vpc_name`: `project-dev-main-vpc`

## Steps: 手順書一覧

1. [[0101] VPCを作成する](../runbooks/0101-create-vpc.md)
2. [[0102] VPC属性を設定する](../runbooks/0102-modify-dns-hostname.md)

# EOD

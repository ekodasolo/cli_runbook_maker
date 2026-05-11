# KMS鍵の作成

## About
S3バケットの暗号化など様々な用途で利用するKMS Customer Managed Keyを作成する


## Why: 作業の目的
S3バケットのオブジェクトをデフォルトで暗号化しデータを保護する目的でKMS鍵を利用する。データレイクの他、CI/CDパイプラインでのアーティファクトバケットの保護にも利用する。

## What: 操作するもの
作成するリソースは以下。すべて東京リージョン（ap-northeast-1）に作成する。
envはdev/prodのいずれかが入る。

|  Name                              |  用途                                 | 備考                            |
| ---------------------------------- | ------------------------------------- | ------------------------------- |
| aone4s-{env}-prep-key              | Preprocess Bucket Key                 |                                 |
| aone4s-{env}-datalake-key          | Data Lake  Bucket Key                 |                                 |
| aone4s-{env}-tfartifact-key        | CI/CD Artifact Bucket Key (Terraform) | 開発環境のみが対象                |
| aone4s-{env}-etlartifact-key       | CI/CD Artifact Bucket Key (ETL)       | 本番環境ではクロスアカウントになる  |

## Who: 作業者の前提

1. Unixシェルの基本操作ができること
1. AWS CLIの基本操作ができること
1. KMSへのアクセス権があること(KMSは特権アクセスが必要)


## Where: 作業環境の条件

- CloudShellに接続し、CloudShell上で作業することを前提とする
- 必要な権限をもったIAM User/Iam RoleでCloudShellを立ち上げる


## 基本仕様

- KMSでCustomer Managedな対象鍵を作成する
- 主にS3バケットでのSSE-KMSで使用する
- 鍵にエイリアスを指定する
- Key Policyでアクセスをコントロールする

## 詳細手順

1. [KMS鍵を作成する](./runbooks/common-0201-CreateKMSKey-runbook.md)
1. [Aliasを作成する](./runbooks/common-0202-CreateKeyAlias-runbook.md)


# EOD

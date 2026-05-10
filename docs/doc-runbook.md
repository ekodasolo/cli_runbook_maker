# ランブック定義の書き方ガイド

## 概要

ランブック定義は YAML ファイル1つで1つの AWS リソース操作を記述する。テンプレートとスニペットの組み合わせを宣言するだけで、完全な Markdown 手順書が生成される。

このドキュメントでは、ランブック YAML の全フィールドの意味と書き方、パラメータ設計の考え方、実践的な Tips を解説する。

## YAML スキーマ

### 全体構造

```yaml
runbook:
  # --- 必須フィールド ---
  id: "0301"
  title: "S3 バケットを作成する"
  about: |
    手順の概要。複数行で書ける。
  operation: CREATE
  template: runbook

  before:
    - 事前に満たすべき条件1
  after:
    - 完了時に期待される状態1

  main:
    snippet: snippets/s3/create-bucket.md

  # --- 任意フィールド ---
  services:
    - S3
  duration: "3 Min"

  pre_checks:
    - title: "事前確認タイトル"
      description: |
        確認内容の説明。
      snippet: snippets/s3/head-bucket.md

  post_checks:
    - title: "事後確認タイトル"
      description: |
        確認内容の説明。
      snippet: snippets/s3/head-bucket.md

  params_files:
    - ../params/training-s3.yaml

  params:
    key: value

  navigation:
    next:
      title: "次の手順書タイトル"
      link: "./0302-enable-s3-versioning.md"
```

### フィールド一覧

| フィールド | 必須 | 型 | 説明 |
| --- | --- | --- | --- |
| `id` | Yes | 文字列 | 4桁の識別番号。サービスごとにプレフィックスが決まっている |
| `title` | Yes | 文字列 | 手順書のタイトル。生成物の `# [ID] タイトル` に展開される |
| `about` | Yes | 文字列 | 手順の概要。`\|` ブロックスカラーで複数行記述が可能 |
| `operation` | Yes | 文字列 | 操作タイプラベル。`CREATE` / `MODIFY` / `DELETE` |
| `template` | Yes | 文字列 | 使用テンプレート名。通常は `runbook` を指定 |
| `before` | Yes | リスト | 事前に満たすべき条件。各項目が番号付きリストとして展開される |
| `after` | Yes | リスト | 完了時に期待される状態。各項目が番号付きリストとして展開される |
| `main` | Yes | オブジェクト | 主処理。`snippet` キーでスニペットパスを指定 |
| `services` | No | リスト | 関連 AWS サービス名（ドキュメント用、生成には影響しない） |
| `duration` | No | 文字列 | 想定所要時間（ドキュメント用、生成には影響しない） |
| `pre_checks` | No | リスト | 事前確認ブロック。1.2, 1.3, ... として展開される |
| `post_checks` | No | リスト | 事後確認ブロック。3.1, 3.2, ... として展開される |
| `params_files` | No | リスト | 共通パラメータファイルのパス（runbook YAML からの相対パス） |
| `params` | No | オブジェクト | この手順書固有のパラメータ。`params_files` より優先 |
| `navigation` | No | オブジェクト | 後続手順書へのリンク |

## 各フィールドの詳細

### id

4桁の文字列で、サービスごとのプレフィックスで分類する。

| プレフィックス | サービス |
| --- | --- |
| `01xx` | EC2 (VPC) |
| `02xx` | SSM Parameter Store |
| `03xx` | S3 |
| `04xx` | KMS |
| `05xx` | CloudFormation |
| `06xx` | DynamoDB |

連番は操作の実行順に振る。例: `0301`（バケット作成） → `0302`（バージョニング） → `0303`（暗号化）。

YAML 上では必ず文字列として記述する（`"0301"` のようにクォートする）。クォートしないと YAML パーサが数値 `301` として解釈する。

### title

手順書のタイトル。生成物では `# [0301] S3 バケットを作成する` のように ID と組み合わせて見出しになる。

命名規約: `{サービス名} {リソース} を {動詞}する` の形式で統一する。

```yaml
# 良い例
title: "S3 バケットを作成する"
title: "DynamoDB GSI を追加する"
title: "CFn スタックを削除する"

# 悪い例（動詞が不明確）
title: "S3 バケットの設定"
title: "DynamoDB テーブル操作"
```

### about

手順の概要を記述する。`|` ブロックスカラーで書き、複数段落に分けてよい。

```yaml
about: |
  DynamoDB テーブル作成の CLI 手順書。

  本手順では、オンデマンドキャパシティモードのテーブルを作成する。
  パーティションキー PK（文字列）とソートキー SK（文字列）の
  複合キー構成で、Single Table Design を想定した汎用スキーマとする。
```

1段落目は「何の手順書か」を端的に書き、2段落目以降で具体的な構成や前提を説明する。

### operation

操作タイプのラベル。生成物の `#### 2.1 リソースの操作 (CREATE)` に展開される。

| 値 | 意味 | 使う場面 |
| --- | --- | --- |
| `CREATE` | 新規リソースの作成 | バケット作成、テーブル作成、スタック作成 |
| `MODIFY` | 既存リソースの属性・設定変更 | バージョニング設定、GSI 追加、Change Set 実行 |
| `DELETE` | リソースの削除 | スタック削除 |

判断に迷う例:

- ラベル・タグの付与 → `MODIFY`（リソース自体の属性変更）
- GSI の追加 → `MODIFY`（テーブルの構成変更）
- TTL の設定 → `MODIFY`（テーブルの設定変更）

### before / after

`before` は作業開始前に満たすべき条件、`after` は作業完了後に期待される状態。各項目は Markdown の番号付きリストとして展開される。

```yaml
before:
  - テーブルが ACTIVE 状態であること（0601 が完了済み）。
after:
  - GSI が ACTIVE 状態であること。
  - GSI のキースキーマが GSI1PK(HASH) + GSI1SK(RANGE) であること。
```

Tips:
- 前提条件に先行手順書がある場合は、ID を括弧内に記載する（例: `0601 が完了済み`）
- `after` の条件は `post_checks` で実際に確認する内容と対応させる
- 1項目1文で簡潔に書く

### template

使用テンプレート名。`templates/<value>.md.j2` として解決される。

現在は汎用テンプレート `runbook` の1つだけが存在し、すべてのランブックで共通して使用する。新しいサービスやリソースを追加する場合もこの値は変えない。

```yaml
template: runbook    # → templates/runbook.md.j2
```

### pre_checks / post_checks

事前確認・事後確認のリスト。各項目は `title`（必須）、`description`（任意）、`snippet`（任意）を持つ。

```yaml
pre_checks:
  # title + description + snippet（フル指定）
  - title: "同名バケットの非存在確認"
    description: |
      作成対象のバケットがまだ存在しないことを確認する。
      404 エラーが返れば期待通り。
    snippet: snippets/s3/head-bucket.md

  # title + snippet（description なし）
  - title: "バケット数の確認"
    snippet: snippets/s3/list-buckets.md

  # title + description のみ（snippet なし、テキスト説明だけ）
  - title: "依存リソースの確認"
    description: 依存するリソースは無い。
```

セクション番号の自動採番:
- `pre_checks` は 1.2, 1.3, ... で採番される（1.1 はパラメータ表が占有）
- `post_checks` は 3.1, 3.2, ... で採番される

中立チェックスニペットの使い分け:

同じスニペット（例: `head-bucket.md`）を pre_check と post_check の両方で使える。「どちらの結果を期待するか」は `description` で案内する。

```yaml
# CREATE の場合
pre_checks:
  - title: "同名バケットの非存在確認"
    description: |
      作成対象のバケットがまだ存在しないことを確認する。
      404 エラーが返れば期待通り。          # ← 非存在を期待
    snippet: snippets/s3/head-bucket.md

post_checks:
  - title: "バケットの作成確認"
    description: |
      バケットが正常に作成され、アクセス可能であることを確認する。
      出力なしで正常終了すれば期待通り。    # ← 存在を期待
    snippet: snippets/s3/head-bucket.md
```

### main

主処理のスニペットを指定する。構造は固定。

```yaml
main:
  snippet: snippets/s3/create-bucket.md
```

`main` に指定するスニペットは、リソースの作成・変更・削除を実行するコマンドを含む。非同期操作の場合は `wait` コマンドもスニペット内に含まれている。

### params_files

共通パラメータファイルのパス。パスは **runbook YAML からの相対パス**で解決される（`generate.py` の実行ディレクトリには依存しない）。

```yaml
params_files:
  - ../params/training-s3.yaml       # runbook YAML の1つ上の params/ を参照
```

複数指定した場合は上から順にマージされ、後のファイルが優先（後勝ち）。

```yaml
params_files:
  - ../params/base.yaml              # ベース値
  - ../params/training-s3.yaml       # S3 固有値（同キーがあれば上書き）
```

各ファイルはトップレベルに `params:` キーを持つ必要がある:

```yaml
# examples/params/training-s3.yaml
params:
  region: ap-northeast-1
  bucket_name: project-dev-training-bucket
```

### params

この手順書固有のパラメータ。`params_files` でマージされた値に対して最優先で上書きされる。

```yaml
params:
  lifecycle_rule_id: expire-objects
  lifecycle_prefix: ""
  lifecycle_expiration_days: "90"
```

固有パラメータがない場合は空オブジェクトを書く:

```yaml
params: {}
```

パラメータの型とテンプレートでの表示:

| 型 | YAML での書き方 | 1.1 パラメータ表での表示 |
| --- | --- | --- |
| スカラー（文字列/数値） | `region: ap-northeast-1` | 通常テーブルの1行 |
| 文字列リスト | `labels: [v1, v2]` | `join(', ')` で結合して通常テーブルに表示 |
| 辞書リスト | 下記参照 | 専用サブテーブルで表示 |

辞書リストの記述例（CloudFormation のスタックパラメータ）:

```yaml
params:
  stack_parameters:
    - key: Environment
      value: dev
    - key: VpcCidr
      value: "10.0.0.0/16"
```

辞書リストは 1.1 パラメータ表で `| ParameterKey | ParameterValue |` 形式の専用サブテーブルとして表示される。

### navigation

後続手順書へのリンク。シーケンスの途中にある手順書で指定する。

```yaml
navigation:
  next:
    title: "S3 バケットのバージョニングを有効にする"
    link: "./0302-enable-s3-versioning.md"
```

`link` は生成物（`.md`）への相対パスを書く。生成物は同じ `dist/runbooks/` ディレクトリに出力されるため、`./` で始まるパスになる。

シーケンスの最後の手順書では `navigation` キー自体を省略する。テンプレートは `{% if navigation.next %}` で条件分岐しているため、省略すれば Navigation セクションは出力されない。

## パラメータ設計の指針

### マージの全体像

```
params_files[0]     （ベース）
  ↓ 上書きマージ
params_files[1]     （後勝ち）
  ↓ 上書きマージ
params               （最優先）
  ↓ コンテキスト注入
テンプレート + スニペット
```

### params_files と params の使い分け

| 値の性質 | 置き場所 | 例 |
| --- | --- | --- |
| 複数ランブックで共通 | `params_files` | `region`, `bucket_name`, `table_name` |
| そのランブックでのみ使用 | `params` | `lifecycle_rule_id`, `gsi_name`, `attribute` |

### params_files の分離基準

サービスドメイン単位で分離する。1.1 のパラメータ表に、そのランブックと無関係な値が表示されないようにするため。

```
examples/params/
  training-common.yaml     # region, vpc_cidr, vpc_name          → 01xx
  training-ssm.yaml        # region, parameter_namespace          → 02xx
  training-s3.yaml         # region, bucket_name                  → 03xx
  training-kms.yaml        # region, key_description, key_alias   → 04xx
  training-cfn.yaml        # region, stack_name, template_url     → 05xx
  training-dynamodb.yaml   # region, table_name                   → 06xx
```

`region` のように複数ドメインで共通の値があっても、それぞれのファイルに重複して書く。1つの params ファイルにまとめるとパラメータ表に無関係な値が混ざるため、可読性を優先する。

### 例示出力のためだけに必要なパラメータ

スニペットの結果例で Jinja2 変数を使っている場合、実際のコマンドには不要でもランブック YAML の `params` に値を定義する必要がある。未定義のままだと空文字で展開される。

```yaml
params:
  # parameter_value はラベル付与コマンドには不要だが、
  # get-parameter-history の結果例で使うため指定する
  parameter_value: db.example.internal
```

YAML 側にコメントで「例示出力用」と明記しておくと保守時に意図がわかりやすい。

### 値の記述規約

JSON リテラルとしてコマンドに埋め込まれるパラメータは、文字列として書く:

```yaml
# OK: 文字列として扱われ、JSON リテラルの "true" と一致する
value: "true"

# NG: Python の bool になり、Jinja2 で "True" に変換される
value: true

# OK: 整合性のため数値も文字列推奨
lifecycle_expiration_days: "90"
```

理由: YAML の `true` は Python の `True` になり、`str(True)` は `"True"` を返す。JSON リテラルの `true`（小文字）と不一致になる。

## 操作タイプ別のパターン

### CREATE パターン

新規リソースを作成する手順書の典型構成。

```yaml
runbook:
  operation: CREATE

  before:
    - 同名のリソースが存在しないこと。
  after:
    - リソースが作成されていること。

  pre_checks:
    - title: "リソース数の上限確認"          # 任意
      snippet: snippets/{service}/list-xxx.md
    - title: "同名リソースの非存在確認"
      description: |
        エラーが返れば作成可能。            # ← 非存在を期待する案内
      snippet: snippets/{service}/describe-xxx.md

  main:
    snippet: snippets/{service}/create-xxx.md

  post_checks:
    - title: "リソースの作成確認"
      description: |
        正常に出力されれば期待通り。        # ← 存在を期待する案内
      snippet: snippets/{service}/describe-xxx.md
```

ポイント: pre_check と post_check で同じ中立チェックスニペットを使い、`description` で期待する結果を案内する。

### MODIFY パターン

既存リソースの属性・設定を変更する手順書。

```yaml
runbook:
  operation: MODIFY

  before:
    - 対象リソースが存在すること。
  after:
    - 設定が変更されていること。

  pre_checks:
    - title: "対象リソースの存在確認"
      snippet: snippets/{service}/describe-xxx.md
    - title: "現在の設定確認"                # 任意（変更前の状態確認）
      snippet: snippets/{service}/get-xxx.md

  main:
    snippet: snippets/{service}/put-xxx.md

  post_checks:
    - title: "変更後の設定確認"
      snippet: snippets/{service}/get-xxx.md   # pre_check と同じ get 系
```

ポイント: 変更前後の状態を同じ get 系スニペットで確認することで、差分がわかりやすくなる。

### DELETE パターン

リソースを削除する手順書。CREATE の逆パターン。

```yaml
runbook:
  operation: DELETE

  before:
    - 削除対象のリソースが存在すること。
  after:
    - リソースが削除されていること。

  pre_checks:
    - title: "削除対象リソースの確認"
      description: |
        リソースが存在し、その状態を確認する。   # ← 存在を期待
      snippet: snippets/{service}/describe-xxx.md

  main:
    snippet: snippets/{service}/delete-xxx.md

  post_checks:
    - title: "リソース削除の確認"
      description: |
        エラーが返れば削除完了。                   # ← 非存在を期待
      snippet: snippets/{service}/describe-xxx.md
```

ポイント: post_check では非存在側の結果を期待する。

## ファイルの命名規則

### ランブック YAML

```
{4桁ID}-{動詞}-{リソース概要}.yaml
```

動詞の選択:

| 動詞 | 用途 | 例 |
| --- | --- | --- |
| `create` | 新規作成 | `0301-create-s3-bucket.yaml` |
| `enable` | 機能の有効化 | `0302-enable-s3-versioning.yaml` |
| `configure` | 設定の適用 | `0303-configure-s3-encryption-sse-s3.yaml` |
| `update` | 値の更新 | `0203-update-ssm-parameter-db-host.yaml` |
| `label` | ラベル付与 | `0204-label-ssm-parameter-db-host.yaml` |
| `execute` | 実行 | `0503-execute-cfn-change-set.yaml` |
| `delete` | 削除 | `0504-delete-cfn-stack.yaml` |

### 配置場所

ランブック YAML は `<project>/runbooks/` 直下に配置する。`<project>` は `runbooks/` を含む任意のディレクトリ（例では `examples/`）。

```
examples/
  runbooks/
    0301-create-s3-bucket.yaml
    0302-enable-s3-versioning.yaml
    ...
  params/
    training-s3.yaml
    ...
  dist/runbooks/
    0301-create-s3-bucket.md       # ← 生成物
    0302-enable-s3-versioning.md
    ...
```

## 実践的な Tips

### 手順書シーケンスの設計

関連する手順書は ID の連番と `navigation` で繋げてシーケンスにする。

```
0301 → 0302 → 0303 → 0304 → 0305 → 0306
 CREATE  MODIFY  MODIFY  MODIFY  MODIFY  MODIFY
 (nav→)  (nav→)  (nav→)  (nav→)  (nav→)  (navなし)
```

最後の手順書では `navigation` を省略する。

### スニペットの選択

ランブック YAML では既存のスニペットの中から適切なものを選んで使う。対応するスニペットがない場合は、先にスニペットを作成する。

スニペットのパスは `snippets/` から始まる相対パスで記述する:

```yaml
snippet: snippets/s3/head-bucket.md
```

### 辞書リストパラメータの注意

`stack_parameters` のような辞書リストを使うスニペットは、その変数が未定義の場合にも正常動作するよう設計されている（`{% if stack_parameters %}` ガード）。未使用の場合は `params` から省略して構わない。

例示出力で辞書リストの内容を表示したい場合（例: DELETE 手順書で削除前の最終状態を示す）は、コメントで意図を明記する:

```yaml
params:
  stack_parameters:  # 例示出力用（削除前の最終状態）
    - key: Environment
      value: staging
```

### 配列型パラメータ値

CloudFormation の `CommaDelimitedList` のように、カンマ区切りで複数値を渡す場合は YAML のリスト構文を使う:

```yaml
params:
  stack_parameters:
    - key: AllowedCidrs
      value:
        - "10.0.0.0/16"
        - "172.16.0.0/12"
```

スニペット側のフィルタ（`join(',')` + 型判定）により、`10.0.0.0/16,172.16.0.0/12` に展開される。

### よくある間違い

1. **id をクォートしない**: `id: 0301` → 数値 `301` として解釈される。必ず `id: "0301"` と書く

2. **params_files のパスを cwd 基準で書く**: パスは runbook YAML からの相対パスで解決される。`generate.py` の実行ディレクトリには依存しない

3. **before/after に一般的すぎる条件を書く**: 具体的なリソース名や状態を明記する。「リソースが準備済みであること」ではなく「テーブルが ACTIVE 状態であること（0601 が完了済み）」

4. **description をスニペット側の責務と混同する**: スニペットは中立的な結果例を示す。「どちらの結果を期待するか」はランブック YAML の `description` で案内する

5. **結果例で使う変数を params に定義し忘れる**: 未定義の Jinja2 変数は空文字に展開される。スニペットの結果例で使われる変数はすべて params（または params_files）で定義すること

6. **navigation.link に YAML のパスを書く**: リンク先は生成物（`.md`）へのパスを書く。`./0302-enable-s3-versioning.md` のように `.md` 拡張子にする

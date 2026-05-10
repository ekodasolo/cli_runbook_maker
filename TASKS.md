# Runbook Toolkit タスクリスト

## フェーズ0: 仕様の簡素化 — 完了

3層構造（シナリオ／手順書／スニペット）から2層構造（手順書／スニペット）に変更し、ツールキット／プロジェクトのリポジトリ分離も廃止した。詳細は SPEC.md 参照。

### 仕様ドキュメントの刷新
- [✓] SPEC.md の刷新（2層構造、シングルリポジトリ、`params_files` 機構、新CLI）
- [✓] TASKS.md の刷新（本ファイル）
- [✓] LOGS.md に簡素化方針の決定を記録

### 実装の追従（feature/cli-simplification）
- [✓] `generate.py` のCLI簡素化
  - [✓] 位置引数で runbook YAML を受け取り（複数可）、`--toolkit`／`--scenario` を廃止
  - [✓] テンプレート・スニペットの探索パスを `generate.py` 隣接ディレクトリに固定
  - [✓] `params_files` フィールドの読み込みとマージ順の実装
  - [✓] 出力先を `<runbook>.parent.parent/dist/runbooks/<basename>.md` に変更
- [✓] `templates/scenario.md.j2` を削除
- [✓] `examples/scenarios/` を削除（手順書一覧の提示は今後 README 等で行う）
- [✓] 旧 `examples/scenarios/0100-create-vpc.yaml` の `params:` を `examples/params/training-common.yaml` に移設
- [✓] `examples/runbooks/*.yaml` に `params_files: [../params/training-common.yaml]` を追記
- [✓] 動作検証：新CLIで `examples/runbooks/*.yaml` を生成し、`examples/dist/runbooks/*.md` が以前と完全一致（`diff -u` で差分なし）することを確認

備考：
- `0101-create-vpc.yaml` の `navigation.next` は元から runbook YAML 側に存在していたため移設不要だった
- 旧 generate.py のシナリオ MD 出力は廃止。フェーズ1の「シナリオMD生成成功」の検証項目はもう該当しない

---

## フェーズ1.5: テンプレート汎化 — 完了

テンプレートが「操作タイプ × 特定リソース」で1対1に貼り付き、新リソースを追加するたびに新テンプレートが要る状態（SPEC §1.1 の「資産として蓄積」方針に反する）を解消した。汎用テンプレート1個 + 役割中立スニペットの組合せに移行済み。

### 設計
- [✓] 汎用テンプレート `templates/runbook.md.j2` を新設（CREATE/MODIFY/DELETE 共通）
- [✓] runbook YAML スキーマに `slug` / `operation` / `shell_vars` / `pre_checks[]` / `main` / `post_checks[]` を導入（SPEC §4.1 更新）
- [✓] スニペット内の変数規約を確立（コマンド本体はシェル変数、例示出力は Jinja 変数。SPEC §6.6 で明文化）
- [✓] パラメータプレビュー（`cat << EOF > $FILE_PARAMETER`）ブロックは廃止 — 0102 で破綻していたため
- [✓] 1.1 の `RUNBOOK_TITLE` を `slug` から生成（既知課題「日本語タイトルが混入」を解消）

### 実装
- [✓] `templates/runbook.md.j2` を作成（pre_checks/post_checks の自動採番、shell_vars ループ展開）
- [✓] スニペット新設：`list-vpcs.md` / `find-vpc-id-by-cidr.md` / `describe-vpc-dns-attributes.md`
- [✓] 既存スニペット書き換え（コマンドをシェル変数化）：`create-vpc.md` / `describe-vpcs.md` / `modify-vpc-attribute.md` / `describe-vpc-attribute.md`
- [✓] `examples/runbooks/0101-create-vpc.yaml` を新スキーマに移行
- [✓] `examples/runbooks/0102-modify-dns-hostname.yaml` を新スキーマに移行
- [✓] 旧テンプレート削除：`templates/ec2-create-vpc.md.j2` / `templates/ec2-modify-vpc-attribute.md.j2`
- [✓] `generate.py` に `params` dict 注入と `shell_var` フィルタを追加

### 検証
- [✓] 既知課題2件の解消を確認
  - 0102 主処理 `--vpc-id ` が空 → `--vpc-id ${VPC_ID}` に修正済み
  - `RUNBOOK_TITLE` 日本語混入 → `0102-modify-dns-hostname` に修正済み
- [✓] 0101 / 0102 の生成物が SPEC §9 の構造に従うことを確認
- [✓] スニペット側の変数規約（コマンド = shell var、例示出力 = Jinja）が両 runbook で機能することを確認

### 残課題（次のタスクで扱う）
- [×] ~~監査ログ用パラメータプレビューブロックの再設計~~ — **不要として閉鎖**。即値レンダリング方針（フェーズ1.6）の下では runbook 自身が記録になるため監査ログは冗長
- [×] ~~`runbook.cleanup` フィールドの導入~~ — **不要として閉鎖**（フェーズ1.7）。実運用で「中間リソースの削除」が必要なケースはまず出てこないため、3.99 セクションごと撤廃
- [✓] 複数 post_check に title/description を持たせる UI — フェーズ1.8 で対応済み

---

## フェーズ1.8: post_check の title/description 対応 — 完了

実運用で複数の post_check が必要なケースがあるという判断に基づき、各 post_check に title（必須）と description（任意）を持たせ、pre_check と対称的に 3.1, 3.2, ... と番号付きセクションで展開できるようにした。

### 設計
- [✓] post_checks は pre_checks と対称的に section 番号 3.1, 3.2, ... で展開
- [✓] title 必須、description 任意（snippet も任意。ただし最低1要素は欲しい運用）
- [✓] section 3 冒頭で `After` 条件を再掲する旧仕様は廃止（When 章にすでにあり、各 post_check の description でカバー可能）
- [✓] post_checks が空のときは `### 3. 後処理` ヘッダだけが残る（authoring 時の指針）

### 実装
- [✓] `templates/runbook.md.j2` の section 3 を pre_checks 風のループに書き換え
- [✓] `examples/runbooks/0101-create-vpc.yaml` / `0102-modify-dns-hostname.yaml` の post_checks に title/description を追加
- [✓] SPEC §4.1（post_checks サンプル）、§9（構造図の 3.X 表記）を更新

### 検証
- [✓] 0101 / 0102 を再生成し、section 3 が `#### 3.1 [title]` から始まり、description → snippet の順に展開されることを確認
- [✓] 連続生成で MD5 一致（冪等性）

---

## フェーズ1.7: 3.99 中間リソース削除セクションの撤廃 — 完了

実運用で「中間リソースの削除」が必要なケースはまず発生しないという判断に基づき、テンプレートから 3.99 セクションを撤廃。

### 実装
- [✓] `templates/runbook.md.j2` から 3.99 セクション（`runbook.cleanup` 参照含む）を削除
- [✓] SPEC §9 の構造図から 3.99 を削除
- [✓] フェーズ1.5 残課題の `runbook.cleanup` フィールド導入タスクを「不要として閉鎖」に変更

### 検証
- [✓] 0101 / 0102 を再生成し、3.99 セクションが消えること、Navigation が直前 section からの空行1つで続くことを確認

---

## フェーズ1.6: 即値レンダリング方針への転換

「runbook は生成されるものなので、コマンド内のパラメータ値は即値（リテラル）で書き出す」方針への転換。シェル変数で抽象化するのは実行時取得値（VPC_ID 等）に限定する。手書き時代の名残（FILE_PARAMETER 監査ログ、shell_vars 代入ブロック）を撤去し、画面に出ているコマンドが流したコマンドそのもの、という1対1対応を確立する。

### 設計
- [✓] スニペット規約：静的設定は Jinja2 即値、実行時取得値は `${VPC_ID}` 等のシェル変数（SPEC §6.6 で明文化）
- [✓] パラメータ値の YAML 表記規約：JSON リテラルと一致する文字列で書く（`value: "true"`、`value: "30"` 等。SPEC §6.7）
- [✓] 1.1 セクションをパラメータ表に統合。FILE_PARAMETER 設定 / shell_vars 代入 / `cat << ETX` 確認ブロックを撤去
- [✓] runbook YAML スキーマから `shell_vars` / `slug` フィールドを撤去

### 実装
- [✓] `templates/runbook.md.j2` の 1.1 セクションをパラメータ表に置き換え
- [✓] スニペット7件を即値ベースに書き換え（`create-vpc.md` / `describe-vpcs.md` / `modify-vpc-attribute.md` / `describe-vpc-attribute.md` / `list-vpcs.md` / `find-vpc-id-by-cidr.md` / `describe-vpc-dns-attributes.md`）
- [✓] `examples/runbooks/0101-create-vpc.yaml` / `0102-modify-dns-hostname.yaml` から `shell_vars` / `slug` 撤去、`value: "true"` を文字列化
- [✓] `generate.py` から不要になった `shell_var` フィルタ撤去、コメントを新仕様に合わせて修正
- [✓] SPEC §4.1（YAML スキーマ）、§6.4（テンプレートの責務）、§6.6（変数規約）、§6.7（YAML 表記規約）、§9（生成構造）、§9.1（パラメータ表）を更新

### 検証
- [✓] 0101 / 0102 の生成物が即値で出力されることを確認（`--cidr-block 10.0.0.0/24`、`--region ap-northeast-1` 等）
- [✓] 0102 の主処理コマンドで `${VPC_ID}` のみシェル変数、その他は即値で出力されることを確認
- [✓] 1.1 のパラメータ表とコマンド本体の値が一致することを確認（`value: true` の表記不一致を修正済み）
- [✓] 連続生成で MD5 一致（冪等性）

---

## フェーズ1: プロトタイプ（VPC作成シナリオ）— 完了

### スニペット作成
- [x] `snippets/ec2/create-vpc.md`
- [x] `snippets/ec2/describe-vpcs.md`
- [x] `snippets/ec2/describe-vpc-attribute.md`
- [x] `snippets/ec2/modify-vpc-attribute.md`

### テンプレート作成
- [x] `templates/ec2-create-vpc.md.j2`
- [x] `templates/ec2-modify-vpc-attribute.md.j2`

### サンプルYAML作成
- [x] `examples/scenarios/0100-create-vpc.yaml`（フェーズ0で廃止予定）
- [x] `examples/runbooks/0101-create-vpc.yaml`
- [x] `examples/runbooks/0102-modify-dns-hostname.yaml`

### 生成ツール実装
- [✓] `generate.py` の基本実装（フェーズ0でCLIを刷新予定）
  - [✓] YAML読み込み（シナリオ・手順書）
  - [✓] パラメータ解決（シナリオ共通 → 手順書固有のマージ）
  - [✓] テンプレート解決（プロジェクト側 → 共通側のフォールバック）※フェーズ0で固定パスに簡素化
  - [✓] Jinja2によるMarkdown生成
  - [✓] スニペットのinclude展開

### 検証
- [✓] VPC作成シナリオのMarkdown生成（成功：`examples/dist/scenarios/0100-create-vpc.md` ほか2件を生成）
- [×] ~~生成物と現行手順書（0101-CreateVPC-Runbook.md, 0102-ModifyDNSHostname-Runbook.md）の比較確認~~ — **不要として閉鎖**。フェーズ1.5〜1.8 で構造を大幅に変更したため現行手書き版との byte レベル一致は意図しない。目視レビュー済み
- [×] ~~生成物がCloudShellで読みながら実行できる品質であることの確認~~ — **不要として閉鎖**。即値展開、pre/post_check の構造、Navigation すべて正常に出力されることを設計時に確認済み

### 既知の課題 — フェーズ1.5 で解消済み
- ~~`templates/ec2-modify-vpc-attribute.md.j2` で include する `snippets/ec2/modify-vpc-attribute.md` および `describe-vpc-attribute.md` が `{{ vpc_id }}` を要求するが、テンプレート/YAML 側でセットされていないため `--vpc-id ` の値が空になる~~ → スニペットをシェル変数規約に変更し、事前確認で取得した `${VPC_ID}` がそのまま伝播する形に解決
- ~~`templates/ec2-modify-vpc-attribute.md.j2` の `RUNBOOK_TITLE` が `runbook.title | lower | replace(' ', '-')` から生成されているため、日本語タイトルでは使い物にならない~~ → runbook YAML に `slug` フィールドを追加し、`{{ runbook.id }}-{{ runbook.slug }}` で生成する形に解決

---

## フェーズ2.1: SSM 追加テスト（パラメータ更新・ラベル付与） — 完了

フェーズ2 の設計が異なる SSM 操作（CREATE 以外）に通用するかの検証として、UPDATE と LABEL の2 runbook を追加。

### 設計
- [✓] 「1 runbook = 1 リソース」「アトミックスニペット」「即値原則」をそのまま適用
- [✓] `describe-parameter.md` を「存在/非存在の両ケースを例示」する中立形式に書き直す（0201/0202 の create と 0203/0204 の update/label の両方で使えるように）
- [✓] `--overwrite` 用の `put-parameter-overwrite.md` を新スニペットとして分離（`put-parameter.md` との混在を避ける）
- [✓] Navigation を 0201 → 0202 → 0203 → 0204 の線形シーケンスで連結

### 実装
- [✓] `snippets/ssm/describe-parameter.md` を中立化（narrative を「状態を確認」に）
- [✓] `snippets/ssm/put-parameter-overwrite.md` 新設
- [✓] `snippets/ssm/label-parameter-version.md` 新設
- [✓] `snippets/ssm/get-parameter-history.md` 新設
- [✓] `examples/runbooks/0203-update-ssm-parameter-db-host.yaml`
- [✓] `examples/runbooks/0204-label-ssm-parameter-db-host.yaml`
- [✓] `examples/runbooks/0202-create-ssm-parameter-db-port.yaml` の navigation.next を 0203 に追加
- [✓] SPEC §8 に新スニペットを追加

### 検証
- [✓] 全 6 runbook（0101, 0102, 0201, 0202, 0203, 0204）が生成成功
- [✓] 0203 の主処理に `--overwrite` フラグ、Version: 2 への増加が反映
- [✓] 0204 の主処理が `aws ssm label-parameter-version`、post-check で `Labels: ["production-2026-q2"]` 表示
- [✓] Navigation 連鎖（0201→0202→0203→0204）と末尾 0204 で Navigation セクション無し
- [✓] 連続生成で MD5 一致（冪等性）

---

## フェーズ2: SSMパラメータ対応 — 完了

汎用テンプレート（`runbook.md.j2`）をそのまま使い、SSM 用スニペット追加と runbook YAML 作成のみで実現。**スニペットはアトミックに保ち**、複数パラメータ作成は「1 パラメータ = 1 runbook」のスタイルで分割する方針を採用（ループ展開機構は導入しない）。

### 設計
- [✓] スニペットは 1 スニペット = 1 AWS CLI コマンドのアトミック単位を維持
- [✓] 複数リソース操作は複数の runbook YAML に分割（1 runbook = 1 リソース）
- [✓] テンプレート、`generate.py`、YAML スキーマには変更を入れない方針
- [✓] Navigation セクションを `navigation.next` がある場合のみ出力するように改善（シーケンス末尾の runbook で空セクションが出ない）
- [✓] params ファイルは VPC 系（`training-common.yaml`）と SSM 系（`training-ssm.yaml`）で分離。1.1 のパラメータ表に runbook 実態と関係ない値が出ないようにする
- [✓] VPC 系（0101, 0102）と SSM 系（0201, 0202）は独立シーケンスとして扱う（VPC の navigation は SSM に繋げない）

### 実装
- [✓] `snippets/ssm/describe-parameter.md` — 指定名のパラメータの非存在確認
- [✓] `snippets/ssm/put-parameter.md` — パラメータ1件を作成
- [✓] `snippets/ssm/get-parameter.md` — パラメータの値を取得
- [✓] `examples/params/training-ssm.yaml` — SSM 用共通パラメータ
- [✓] `examples/runbooks/0201-create-ssm-parameter-db-host.yaml`
- [✓] `examples/runbooks/0202-create-ssm-parameter-db-port.yaml`
- [✓] `templates/runbook.md.j2` — Navigation セクションを条件付き化
- [✓] SPEC §8 を更新（実装済みスニペット一覧に SSM 系を追加、アトミック原則を明記）

### 検証
- [✓] 全 4 runbook（0101, 0102, 0201, 0202）の生成成功
- [✓] 0201 の即値展開が正常（`--name /myapp/training/db/host` 等）
- [✓] 0202 で Navigation セクションが出力されない（シーケンス末尾）
- [✓] 0101 / 0102 の Navigation セクションは引き続き出力される（後方互換）
- [✓] 連続生成で MD5 一致（冪等性）

## 将来のタスク（実装は後回し）

### スニペット変数のバリデーション機構

#### 背景
スニペットと runbook の interface は Jinja2 変数（生成時）とシェル変数（実行時）の2層で、いずれも「規約」だけの疎結合（型・スキーマなし）。現状、生成時に2種類の typo が silently 通る：

- **A. snippet 側の typo**：snippet に `{{ regoin }}` のような誤記。生成 MD に `--region ` のような空欄が残る
- **B. runbook 側の missing param**：snippet が必要とする変数を runbook が提供していない。同じく空欄になる

snippet 数や書き手が増えると、目視レビューで catch しきれなくなる。

#### 採用方針
**vars.yaml + StrictUndefined の組み合わせ** を採用する。

- `snippets/{service}/vars.yaml` で「この service で使ってよい変数」を service 単位で宣言（A を catch、語彙の文書化を兼ねる）
- Jinja2 の `Environment` を `undefined=StrictUndefined` に切り替え（B を catch）

#### vars.yaml の形式（案）

```yaml
# snippets/ssm/vars.yaml
vars:
  - name: parameter_name
    description: SSM パラメータの完全名（例: /myapp/training/db/host）
  - name: parameter_type
    description: SSM パラメータの型（String / StringList / SecureString）
  - name: parameter_value
    description: 設定する値
  - name: parameter_description
    description: パラメータの説明文
  - name: parameter_labels
    description: ラベルのリスト
  - name: region
    description: 対象リージョン
```

#### 実装サブタスク
- [ ] `snippets/ec2/vars.yaml` / `snippets/ssm/vars.yaml` の作成
- [ ] `generate.py` に snippet 内 `{{ X }}` 抽出ロジックを追加
- [ ] `generate.py` で snippet が参照する変数を service の vars.yaml と突合し、未宣言変数があればエラー
- [ ] `generate.py` の Jinja2 Environment を `undefined=StrictUndefined` に切り替え
- [ ] `templates/runbook.md.j2` の optional フィールドアクセス（`{% if check.description %}` 等）を StrictUndefined と両立する形に書き換え（`'description' in check` 等）
- [ ] SPEC §6.6 に validation 方針の節を追記

#### 検討から外した代替案
- **snippet ごとの YAML frontmatter で required vars 宣言**：粒度はより精確になるが、snippet ファイルに YAML が混じることで Markdown としての可読性が下がる。service 単位で十分と判断
- **vars.yaml だけで済ませる**：A しか catch できない。B が見逃しのままになるので不採用

#### 実施タイミング
- snippet が 30 件を超えるあたり、または書き手が複数になった時点で着手するのが妥当
- 現状（snippet 14 件、書き手少数）は目視レビューで賄えており、今は YAGNI

---

## フェーズ3: S3 対応 — 完了

汎用テンプレート（`runbook.md.j2`）をそのまま使い、S3 用スニペット追加と runbook YAML 作成のみで実現。複雑な JSON ドキュメント（ライフサイクル設定、バケットポリシー）には `file://` パターン（§6.7）を導入。

### 設計
- [✓] `file://` パターンの導入（JSON ドキュメントをヒアドキュメントで一時ファイルに書き出し、`file://` で参照）
- [✓] SSE-S3 / SSE-KMS を別スニペットに分離（同一 CLI コマンドだが JSON ペイロードが異なるため）
- [✓] `head-bucket.md` を中立形式に（SSM の `describe-parameter.md` と同様、存在/非存在の両方を例示）
- [✓] テンプレート、`generate.py` への変更なし

### 実装
- [✓] スニペット12件新設（`snippets/s3/`）:
  - `list-buckets.md` / `head-bucket.md` / `create-bucket.md`
  - `get-bucket-versioning.md` / `put-bucket-versioning.md`
  - `get-bucket-encryption.md` / `put-bucket-encryption-sse-s3.md` / `put-bucket-encryption-sse-kms.md`
  - `get-bucket-lifecycle-configuration.md` / `put-bucket-lifecycle-configuration.md`（`file://` パターン）
  - `get-bucket-policy.md` / `put-bucket-policy.md`（`file://` パターン）
- [✓] `examples/params/training-s3.yaml` 新設
- [✓] ランブック6件新設:
  - `0301-create-s3-bucket.yaml` (CREATE)
  - `0302-enable-s3-versioning.yaml` (MODIFY)
  - `0303-configure-s3-encryption-sse-s3.yaml` (MODIFY)
  - `0304-configure-s3-encryption-sse-kms.yaml` (MODIFY)
  - `0305-configure-s3-lifecycle.yaml` (MODIFY, `file://` パターン)
  - `0306-configure-s3-bucket-policy.yaml` (MODIFY, `file://` パターン)
- [✓] Navigation 連鎖: 0301 → 0302 → 0303 → 0304 → 0305 → 0306
- [✓] SPEC §6.7 に `file://` パターンの節を追加、§8 に S3 スニペット一覧を追加

### 検証
- [✓] 全 12 runbook（0101-0306）の生成成功
- [✓] `file://` パターン（0305, 0306）でヒアドキュメント + CLI コマンドの2ステップ構成が正常出力
- [✓] インラインパターン（0303, 0304）で JSON がコマンドに正常埋込
- [✓] Navigation 連鎖（0301→0302→0303→0304→0305→0306）と末尾 0306 で Navigation セクション無し
- [✓] 連続生成で MD5 一致（冪等性）
- [✓] 既存ランブック（0101-0204）への影響なし

---

## フェーズ3+: KMS 対応 — 完了

汎用テンプレート（`runbook.md.j2`）をそのまま使い、KMS 用スニペット追加と runbook YAML 作成のみで実現。`key_ref` パラメータにより、実行時取得値（`${KEY_ID}`）と静的エイリアス（`alias/xxx`）を同一スニペットで扱えるパターンを導入。キーポリシー設定には `file://` パターン（§6.7）を適用。

### 設計
- [✓] `key_ref` パラメータパターンの導入（KeyId シェル変数 / エイリアスのいずれも同一スニペットで対応）
- [✓] ランブック間の値伝播設計（0401 で KEY_ID 取得 → 0402 でシェル変数参照 → 0403 でエイリアス参照）
- [✓] `file://` パターンでキーポリシー設定（3 Statement: Root/Admin/Usage）
- [✓] テンプレート、`generate.py` への変更なし

### 実装
- [✓] スニペット7件新設（`snippets/kms/`）:
  - `list-keys.md` — リージョン内のキー一覧
  - `create-key.md` — キー作成（KEY_ID をシェル変数に取得）
  - `describe-key.md` — キー詳細確認（中立、`key_ref` パラメータ）
  - `list-aliases.md` — エイリアス一覧（中立、設定/未設定の両例）
  - `create-alias.md` — エイリアス設定
  - `get-key-policy.md` — キーポリシー確認（`jq` でパース）
  - `put-key-policy.md` — キーポリシー設定（`file://` パターン）
- [✓] `examples/params/training-kms.yaml` 新設
- [✓] ランブック3件新設:
  - `0401-create-kms-key.yaml` (CREATE)
  - `0402-create-kms-alias.yaml` (MODIFY)
  - `0403-configure-kms-key-policy.yaml` (MODIFY, `file://` パターン)
- [✓] Navigation 連鎖: 0401 → 0402 → 0403
- [✓] SPEC §8 に KMS スニペット一覧を追加

### 検証
- [✓] 全 15 runbook（0101-0403）の生成成功
- [✓] `${KEY_ID}` が Jinja2 に解釈されずリテラルとして出力（0401, 0402）
- [✓] 0403 で `alias/project-dev-training-key` が即値として出力
- [✓] `file://` パターン（0403）でヒアドキュメント + jq チェック + CLI の3ステップ構成が正常出力
- [✓] キーポリシー JSON に3つの Statement（Root/Admin/Usage）が正しく展開
- [✓] Navigation 連鎖（0401→0402→0403）と末尾 0403 で Navigation セクション無し
- [✓] 連続生成で差分なし（冪等性）
- [✓] 既存ランブック（0101-0306）への影響なし

---

## フェーズ4: 追加操作タイプ（予定）

- [ ] CloudFormation: スタック作成、変更セット作成、変更セット実行、スタック削除
- [ ] DynamoDB: テーブル作成、GSI作成、TTL設定

# Runbook Toolkit 作業ログ

## 2026-05-10: CloudFormation スタック操作対応（フェーズ4）

### 実施内容
- CloudFormation 用スニペット8件を `snippets/cloudformation/` に新設
  - 従来パターン: `list-stacks.md`、`describe-stacks.md`、`describe-stack-events.md`、`describe-change-set.md`
  - S3 テンプレート参照 + `file://` + ループ + wait パターン: `create-stack.md`
  - `file://` + ループ + wait パターン: `create-change-set.md`
  - wait パターン: `execute-change-set.md`、`delete-stack.md`
- サンプル runbook 4件を作成: `0501-create-cfn-stack.yaml`（CREATE）、`0502-create-cfn-change-set.yaml`（CREATE）、`0503-execute-cfn-change-set.yaml`（MODIFY）、`0504-delete-cfn-stack.yaml`（DELETE）
- CloudFormation 用共通パラメータファイル `examples/params/training-cfn.yaml` を新設
- Navigation 連鎖: 0501 → 0502 → 0503 → 0504
- `templates/runbook.md.j2` の 1.1 パラメータセクションを型ベース2パス振り分けに改修
- スニペット内の `{{ p.value }}` を配列型対応フィルタに置換
- スニペット内のループ変数に `{% if stack_parameters %}` 未指定ガードを追加
- SPEC §8 に CloudFormation スニペット一覧を追加
- KNOWLEDGE.md に新パターン5件（§1.5-1.7、§2.3、§7.5）と TIPS を追記

### 決定事項
- **S3 テンプレート参照方式の採用**。CloudFormation テンプレートは CLI 手順書のスコープ外で管理する前提。`--template-url` で S3 上のテンプレートを参照する方式に統一。テンプレートの作成・修正は別作業として扱う
- **`file://` + Jinja2 ループパターンの導入**。CloudFormation のスタックパラメータは数・名前がランブックごとに異なるため、既存の `file://` パターンと Jinja2 ループを組み合わせる新パターンを設計。runbook YAML で `stack_parameters` リストを定義し、スニペット内で JSON に展開する
- **配列型パラメータ値への対応**。`{{ p.value }}` を `{{ p.value | join(',') if p.value is sequence and p.value is not string else p.value }}` に置換。CloudFormation の `CommaDelimitedList` 型パラメータ（セキュリティグループの CIDR リスト等）に対応
- **ループ変数の未指定ガード**。`stack_parameters` が未定義の場合に空の JSON やオプションが出力されないよう、ループとその依存ブロック全体を `{% if stack_parameters %}` で囲む。ループ単体ではなく、ヒアドキュメント・jq チェック・CLI オプション・結果例のセクションすべてをガード対象とする
- **パラメータテーブルの型ベース2パス振り分け**。`params` の値を（1）スカラー/文字列リスト → 通常テーブル、（2）辞書リスト → `| ParameterKey | ParameterValue |` 形式のサブテーブルに分類表示。20個程度のスタックパラメータがあっても読みやすいテーブル形式にした。振り分けは Jinja2 テンプレート内で2パス構成（分類ループ → 出力ループ）で実装
- **非同期操作パターン（wait コマンド）**。`aws cloudformation wait` をスニペット内に含める。§6.5 の例外規定「関連する一連のコマンド」に該当
- **DELETE 操作タイプの初実装**。post_check で中立チェックスニペットの「非存在」側を期待する、CREATE の逆パターン

## 2026-05-10: KMS キー操作対応（フェーズ3+）

### 実施内容
- KMS 用スニペット7件を `snippets/kms/` に新設
  - 従来パターン: `list-keys.md`、`create-key.md`、`describe-key.md`、`list-aliases.md`、`create-alias.md`、`get-key-policy.md`
  - `file://` パターン: `put-key-policy.md`（3 Statement: Root/Admin/Usage）
- サンプル runbook 3件を作成: `0401-create-kms-key.yaml`（CREATE）、`0402-create-kms-alias.yaml`（MODIFY）、`0403-configure-kms-key-policy.yaml`（MODIFY, `file://` パターン）
- KMS 用共通パラメータファイル `examples/params/training-kms.yaml` を新設
- Navigation 連鎖: 0401 → 0402 → 0403
- SPEC §8 に KMS スニペット一覧を追加、「追加予定」から KMS を除外

### 決定事項
- **`key_ref` パラメータパターンの導入**。KMS キーの参照方法は KeyId（UUID）とエイリアス（`alias/xxx`）の2つがあり、ランブック間で使い分ける必要がある。`key_ref` という単一パラメータでどちらも受け取れるようスニペットを設計した:
  - 0401（キー作成）/ 0402（エイリアス設定）: `key_ref: "${KEY_ID}"` — 実行時取得シェル変数
  - 0403（ポリシー設定）: `key_ref: "alias/project-dev-training-key"` — エイリアス設定後なので即値
  - 同一スニペット `describe-key.md` が両方の文脈で再利用できる
- **ランブック間の値伝播設計**。0401 で `KEY_ID` をシェル変数に取得 → 0402 で `${KEY_ID}` として参照（エイリアス設定前なので KeyId が必要）→ 0403 ではエイリアスが存在するため即値に切り替え。シェル変数は「必要な区間」だけで使い、静的参照に切り替え可能になった時点で即値に戻す
- **キーポリシーに `file://` パターンを適用**。3つの Statement（Root アカウントフルアクセス、管理者ロールのキー管理、利用者ロールの暗号化・復号）を含む JSON はインラインでは可読性が低いため、S3 バケットポリシーと同様に `file://` パターンを採用
- **テンプレート・ジェネレータへの変更なし**。フェーズ2、フェーズ3 に続き、スニペットと runbook YAML の追加だけで新サービスに対応できた

## 2026-05-09: S3 バケット操作対応（フェーズ3）

### 実施内容
- S3 用スニペット12件を `snippets/s3/` に新設
  - 従来パターン（インライン）: `list-buckets.md`、`head-bucket.md`、`create-bucket.md`、`get-bucket-versioning.md`、`put-bucket-versioning.md`、`get-bucket-encryption.md`、`put-bucket-encryption-sse-s3.md`、`put-bucket-encryption-sse-kms.md`、`get-bucket-lifecycle-configuration.md`、`get-bucket-policy.md`
  - `file://` パターン: `put-bucket-lifecycle-configuration.md`、`put-bucket-policy.md`
- サンプル runbook 6件を作成: `0301-create-s3-bucket.yaml`（CREATE）、`0302-enable-s3-versioning.yaml`〜`0306-configure-s3-bucket-policy.yaml`（MODIFY x5）
- S3 用共通パラメータファイル `examples/params/training-s3.yaml` を新設
- Navigation 連鎖: 0301 → 0302 → 0303 → 0304 → 0305 → 0306
- SPEC §6.7 に `file://` パターンの節を新設、§8 に S3 スニペット一覧を追加

### 決定事項
- **`file://` パターンの導入**。CLI オプションに渡す JSON ドキュメントが大きく構造が可変な場合（ライフサイクル設定、バケットポリシー等）は、ヒアドキュメントで一時ファイルを作成し `file://` で参照する。JSON の可読性と CLI コマンドの簡潔性を両立する。§6.5 の例外規定に該当し、1スニペット内に「ファイル作成 + jq チェック + CLI 実行」の3ステップをまとめる
- **`file://` パターンでは `jq` によるフォーマットチェックを必須とする**。ヒアドキュメントの記述ミスや Jinja2 展開後の JSON 構文エラーを、CLI 実行前に検出するため。3ステップ構成: (1) `cat << 'EOF' > /tmp/xxx.json` (2) `jq . /tmp/xxx.json` (3) `aws s3api ... file:///tmp/xxx.json`
- **SSE-S3 / SSE-KMS は別スニペットに分離**。同一 CLI コマンド（`put-bucket-encryption`）だが JSON ペイロードの構造が異なるため、アトミック原則に則り別ファイルとする。`put-parameter.md` と `put-parameter-overwrite.md` の前例と同様
- **`head-bucket.md` は中立形式**。SSM の `describe-parameter.md` と同様、存在/非存在の両方の出力例を示し、create の pre_check にも modify の pre_check にも使い回す
- **インラインと `file://` の使い分け基準**: JSON なしまたは小さく固定構造ならインライン、大きくまたは構造が可変なら `file://`。SPEC §6.7 に基準表を明記
- **バケットポリシーは複合ポリシー（4 Statement）を採用**: (1) 非TLS拒否 (2) 指定KMSキー以外拒否 (3) 指定VPCエンドポイント以外拒否 (4) 指定IAMロール以外のGet拒否。`file://` パターンの価値（JSON の可読性）を活かす実践的な例として機能する
- **テンプレート・ジェネレータへの変更なし**。フェーズ2 と同様、スニペットと runbook YAML の追加だけで新サービスに対応できた。汎用テンプレート設計の妥当性が S3 でも確認された


## 2026-05-09: バリデーション機構の方針決定（将来タスク）

### 実施内容
- snippet と runbook を繋ぐパラメータインターフェイスは Jinja2 変数（生成時）とシェル変数（実行時）の2層で、いずれも「規約」だけの疎結合（型・スキーマなし）であることを再確認
- 生成時に検知できない2種類の typo（snippet 側 typo、runbook 側 missing param）について、validation 機構の必要性を議論
- 採用方針として「**vars.yaml + StrictUndefined の組み合わせ**」を決定。実装は将来タスクとして TASKS.md に登録

### 決定事項
- **service 単位の `vars.yaml`** で「この service で使ってよい変数」を宣言（snippet 側 typo を catch + 語彙の文書化）
- **Jinja2 を `StrictUndefined` モードに切り替え** て runbook 側 missing param を生成時例外化
- snippet 単位の YAML frontmatter による required vars 宣言案は、Markdown 可読性低下と実装コストのため不採用（service 単位で十分という判断）
- 実施タイミングは「snippet 30 件超え or 書き手複数化」が目安。現状（14 件、書き手少数）では目視レビューで賄えており YAGNI


## 2026-05-09: SSM 追加テスト — UPDATE と LABEL（フェーズ2.1）

### 実施内容
- フェーズ2 の設計（汎用テンプレート + アトミックスニペット + 即値原則）が CREATE 以外の SSM 操作にも通用するかの検証として、UPDATE と LABEL の2 runbook を追加
- 新スニペット3件：`put-parameter-overwrite.md`（`--overwrite` 付き）、`label-parameter-version.md`、`get-parameter-history.md`
- 既存スニペット `describe-parameter.md` を中立化（「存在/非存在の両ケースを例示」）し、create 系（0201/0202）と update/label 系（0203/0204）の両方で再利用できるようにした
- 新 runbook 2件：`0203-update-ssm-parameter-db-host.yaml`、`0204-label-ssm-parameter-db-host.yaml`
- Navigation を 0201 → 0202 → 0203 → 0204 の線形シーケンスで連結（0202 の navigation.next を 0203 に追加）
- SPEC §8 に新スニペット情報を反映、describe-parameter の役割記述を中立に書き直し

### 決定事項
- **`describe-parameter.md` は中立形式で1件に集約する**。最初は「不存在を期待」の narrative だったが、update/label でも同じ AWS CLI コマンドで「存在を期待」する場面があるため、両ケースの結果例を併記する形に書き直し。runbook の pre_check description で「どちらを期待するか」を案内する。これでアトミック原則（1 スニペット = 1 AWS CLI コマンド）を保ったまま、複数のユースケースで再利用できる
- **`put-parameter` と `put-parameter-overwrite` は別スニペットに分離**。`--overwrite` フラグの有無で挙動（既存があった場合に上書きするか失敗するか）が変わるため、混在させずに別ファイルにする。スニペット名で意図が明確になり、誤用のリスクも下がる
- **`get-parameter-history.md` の例示出力は2バージョン分を表示**。UPDATE → LABEL の操作後の状態（Version 2 が新値+ラベル、Version 1 が旧値+ラベル無し）を示すことで、操作が成功したときの履歴の見え方を明示する
- **`parameter_value` を 0204（ラベル付与）にも残す**。ラベル付与には value は不要だが、`get-parameter-history.md` の例示出力で値表示に使うため。runbook YAML にコメントで「例示出力用」と明記

### 設計検証
- UPDATE / LABEL という CREATE と異なる操作種別でも、汎用テンプレートと既存スキーマで違和感なく対応できた
- アトミックスニペットの方針（1 スニペット = 1 AWS CLI コマンド）が、操作種別の違い（put + --overwrite、label-parameter-version、get-parameter-history）でも筋を通せる
- 既存の CREATE 系（0201/0202）の生成物は describe-parameter.md の中立化に伴い変化するが、意図通り（pre_check description が両 narrative を案内する形に整合）


## 2026-05-09: SSM パラメータ対応（フェーズ2）

### 実施内容
- SSM Parameter Store 用のスニペット3件を新設：`describe-parameter.md`、`put-parameter.md`、`get-parameter.md`
- サンプル runbook 2件を作成：`0201-create-ssm-parameter-db-host.yaml`、`0202-create-ssm-parameter-db-port.yaml`
- SSM 用共通パラメータファイル `examples/params/training-ssm.yaml` を新設（VPC 系の `training-common.yaml` とは別ファイル）
- `templates/runbook.md.j2` の Navigation セクションを `navigation.next` がある場合のみ出力するように改善
- SPEC §8 に SSM 系スニペットの一覧を追加。アトミック原則と「1 runbook = 1 リソース」方針を明記
- TASKS.md フェーズ2 を完了状態に更新

### 決定事項
- **スニペットはアトミックに保つ**（1 スニペット = 1 AWS CLI コマンド）。複数パラメータの作成は「1 パラメータ = 1 runbook」のスタイルで分割し、ループ展開機構は導入しない。理由：
  - スニペットの独立性が保てる（再利用しやすい）
  - 各 runbook が end-to-end 自己完結（pre/main/post が1リソースに対応）
  - 失敗時の隔離（パラメータ5番目で失敗しても、6番以降に波及しない）
  - YAML 量産のコストは許容範囲（1ファイル30行程度）
- **VPC 系と SSM 系の `params_files` は分離する**。1.1 のパラメータ表に runbook 実態と関係ない値（VPC runbook で SSM 値が出るなど）が出ないようにする。SPEC §5.2 の「業務単位・環境単位で分割してよい」方針と整合
- **VPC 系（0101, 0102）と SSM 系（0201, 0202）は独立シーケンス**。SPEC のオペレーション分類として VPC ネットワーク構築と SSM パラメータ設定は別の作業フローのため
- **Navigation セクションは `navigation.next` がある場合のみ出力**。シーケンス末尾の runbook（例：0202）で空の `#### Navigation` ヘッダだけが残るのを防ぐ

### 設計検証
今回のフェーズで「即値原則 + 汎用テンプレート + アトミックスニペット + 1 runbook 1 リソース」の組み合わせが SSM のような異種リソースで機能することを確認。フェーズ3（S3 / KMS / CloudFormation）も同パターンで対応可能と判断


## 2026-05-09: post_check の title/description 対応（フェーズ1.8）

### 実施内容
- `templates/runbook.md.j2` の section 3 を pre_checks 風のループに書き換え。各 post_check が `#### 3.1 [title]` → description → snippet の順に展開されるようにした
- `examples/runbooks/0101-create-vpc.yaml` / `0102-modify-dns-hostname.yaml` の post_checks に title / description を追加
- SPEC §4.1（YAML サンプル）と §9（生成構造図）を更新
- フェーズ1.5 残課題3件のうち最後の1件を解消し、フェーズ1.5 全体が閉じた

### 決定事項
- **post_checks は pre_checks と対称な構造にする**。section 番号は 3.1, 3.2, ... と昇格させ、`#### 3.1 [post_check.title]` の形で展開する。サブ番号 `3.1.1` 案より読みやすく、authoring 時の認知負荷も下がる
- **`title` は必須、`description` は任意**。section 見出しに使うため title は必須が自然。短い post_check では title だけで意図が伝わるため description は任意
- **section 3 冒頭で `After` 条件を再掲する旧仕様は廃止**。When > After 章に既に書かれており、各 post_check の description で必要に応じて参照すれば十分。重複を減らすことを優先
- **post_checks が空のときは `### 3. 後処理` ヘッダだけが残る**。空の section は authoring 時に「post_check を入れるべき」と気づきやすい指針として機能する。条件付き非表示にはしない


## 2026-05-09: 3.99 中間リソース削除セクションの撤廃（フェーズ1.7）

### 実施内容
- `templates/runbook.md.j2` から 3.99 セクション（`runbook.cleanup` 参照含む）を削除
- SPEC §9 の構造図から `#### 3.99 中間リソースの削除` を削除
- フェーズ1.5 残課題の `runbook.cleanup` フィールド導入タスクを「不要として閉鎖」に変更
- 0101 / 0102 を再生成し、3.99 セクションが消え、post_checks → Navigation の流れが自然になっていることを確認

### 決定事項
- **3.99「中間リソースの削除」セクションは廃止する**。理由：実運用で「中間リソースの削除が必要な runbook」はまず発生しない（運用経験ベースの判断）。常に「今回は特になし」を表示するセクションは読み手にとって意味のある情報がゼロで、固定で出すコストに見合わない
- 仮に将来「クリーンアップが必要な runbook」が出てきたら、その時に YAML スキーマ拡張＋テンプレート対応を別タスクとして追加すれば良い。Y AGNI を優先
- これでフェーズ1.5 の残課題3件のうち2件（監査ログ、cleanup）が「不要として閉鎖」となった。残りは「複数 post_check に title/description を持たせる UI」のみ


## 2026-05-09: 即値レンダリング方針への転換（フェーズ1.6）

### 実施内容
- スニペット内のコマンド表記を「シェル変数 `${VAR}`」から「Jinja2 即値 `{{ var }}`」に戻した。シェル変数は実行時取得値（`${VPC_ID}` 等）に限定する規約を確立
- テンプレートの 1.1 セクションを再設計：FILE_PARAMETER 設定 / shell_vars 代入 / `cat << ETX` 確認の3ブロックを廃止し、`params` から自動生成するパラメータ表に統合
- runbook YAML スキーマから `shell_vars` と `slug` フィールドを撤去
- 0102 の `value: true` を `value: "true"` に文字列化。パラメータ表とコマンド本体の表記の一致を担保（YAML の bool が Python の str() で `True` になりJSONリテラル `true` と乖離する問題への対処）
- `generate.py` から不要になった `shell_var` フィルタを撤去
- SPEC §4.1（YAML スキーマ）、§6.4（テンプレートの責務）、§6.6（変数規約を「即値原則」に全面書き直し）、§6.7（YAML 表記規約を新設）、§9 / §9.1（生成構造とパラメータ表）を更新
- フェーズ1.5 残課題のうち「監査ログ用パラメータプレビューブロックの再設計」は本方針転換に伴い不要として閉鎖

### 決定事項
- **生成パイプラインを前提とすると、コマンド内の値は即値のほうが正しい**。手書き runbook 時代はパラメータ変更コストを下げるためシェル変数で抽象化していたが、生成可能な今はその利点よりも「画面に出ているコマンドが、流したコマンドそのもの」という1対1対応のほうが価値が高い。冗長性は生成側が吸収する
- **シェル変数は「生成時に確定しない値」だけに使う**。具体的には pre_check で AWS から取得する `${VPC_ID}` 等。静的設定（region、vpc_cidr、attribute、cli_option、value 等）は Jinja2 即値で展開する
- **監査ログは不要**。即値で生成された runbook 自身が「何を流したか」の記録になり、実行時取得値は CloudShell のセッション出力（`describe-vpcs` の表示、`echo $VPC_ID` の表示）に出ているため。手書き時代の FILE_PARAMETER パターンは生成パイプラインでは冗長
- **JSON リテラルとしてコマンドに埋め込まれる値は YAML 上で文字列として書く**（`value: "true"`、`value: "30"` 等）。YAML の bool/int をそのまま使うと Python の str() 規則で大文字化や不要なフォーマット差が出る。SPEC §6.7 で明文化
- **shell_vars / slug フィールドは廃止**。即値方針の下では存在意義がない（shell_vars は静的設定の代入に使われていた、slug は FILE_PARAMETER のファイル名生成に使われていた）
- **1.1 のパラメータ表は事前確認の役割を兼ねる**。間違ったアカウント・リージョンで実行しようとしていないか、CloudShell に入った直後に確認するためのプリフライトチェック


## 2026-05-09: テンプレート汎化（フェーズ1.5）

### 実施内容
- テンプレートが「操作タイプ × 特定リソース」で1対1に貼り付いていた状態を解消し、汎用テンプレート1個 + 役割中立スニペットの組合せに移行した
- `templates/runbook.md.j2` を新設。CREATE/MODIFY/DELETE 共通の骨格を持ち、`pre_checks[]` / `main` / `post_checks[]` / `shell_vars` を runbook YAML 側から差し込む構造とした
- runbook YAML スキーマを拡張：`slug`、`operation`、`shell_vars`、`pre_checks[]`、`main`、`post_checks[]` を追加
- スニペット内の変数規約を確立しSPEC §6.6 に明文化：コマンド本体はシェル変数（`${VPC_CIDR}` 等）、例示出力は Jinja 変数（`{{ vpc_cidr }}` 等）
- スニペットを書き換え／追加：
  - 書き換え（コマンドをシェル変数化）：`create-vpc.md`、`describe-vpcs.md`、`modify-vpc-attribute.md`、`describe-vpc-attribute.md`
  - 新設：`list-vpcs.md`（VPC 一覧サマリー）、`find-vpc-id-by-cidr.md`（VPC ID をシェル変数に取得）、`describe-vpc-dns-attributes.md`（DNS 属性確認）
- `generate.py` に最小変更：`params` dict をコンテキストに追加（`shell_vars` の間接参照用）、`shell_var` フィルタを登録、`TOOLKIT_ROOT` を `ASSETS_ROOT` に改名、コメントを日本語で補強
- 旧テンプレート `templates/ec2-create-vpc.md.j2` / `templates/ec2-modify-vpc-attribute.md.j2` を削除
- `examples/runbooks/0101-create-vpc.yaml`、`examples/runbooks/0102-modify-dns-hostname.yaml` を新スキーマに移行
- SPEC §4.1（YAML スキーマ）、§6.2（汎用テンプレート方針）、§6.4（テンプレートの責務）、§6.5（スニペットの責務）、§6.6（変数規約）、§8（拡充計画）を更新

### 決定事項
- **テンプレートは1個の汎用ファイル `runbook.md.j2` に集約する**。理由：CREATE/MODIFY/DELETE の差異は構造ではなく語彙（操作ラベル `(CREATE)` 等）と参照スニペットの違いに収まり、3個に分けても差分はわずかで重複コストが上回る
- **コマンド本体はシェル変数で書く**。理由：（1）`${VPC_ID}` のように事前確認で取得した値を主処理・事後確認に伝播させる経路として自然、（2）読み手が値を書き換えて再実行できる、（3）「`{{ vpc_id }}` が空のまま `--vpc-id ` で出力される」既知バグが構造的に解消する
- **例示出力は Jinja 変数のままにする**。理由：runbook の実設定値（リージョン・CIDR・名前）が結果例に反映されるとリアル化し、読み手が実際の出力と比較しやすい。スニペット作者は標準 param 名（`vpc_cidr`、`vpc_name` など）に依拠することを許容する
- **YAML の `value` は文字列で書く**（例：`value: "true"`）。シェル変数値として展開され、JSON 文字列として埋め込まれるため、Python の bool が `True`（大文字）に変換されると JSON が壊れる
- **`RUNBOOK_TITLE` 生成は YAML の `slug` フィールドから行う**。日本語タイトルを `lower | replace(' ', '-')` で英数字化していた既知課題を解消
- **パラメータプレビュー（`cat << EOF > $FILE_PARAMETER`）ブロックは廃止**。現状の 0102 では preview と execution の値が乖離して既に壊れており、元から監査ログ用途として運用されていたかも怪しい。再導入が必要なら別タスクで設計する（TASKS.md フェーズ1.5「残課題」に記録）
- `generate.py` のコメントは日本語で記述する。ただしエラーメッセージと argparse help は英語のままとする（スタックトレースでの文字化けリスク回避、`--help` の国際的可読性のため）

### 解消した既知課題
- 0102 の主処理 `--vpc-id ` が空の問題
- `RUNBOOK_TITLE="0102-vpc属性を設定する"` の日本語混入問題


## 2026-05-09: 仕様簡素化の実装追従（generate.py 刷新）

### 実施内容
- `generate.py` を新仕様（SPEC §7）に合わせて書き直した
  - 位置引数で runbook YAML を1〜複数受け取る形に変更（`--toolkit` / `--scenario` を撤廃）
  - テンプレート・スニペットの探索パスを `Path(__file__).parent` 直下に固定（`FileSystemLoader([TOOLKIT_ROOT])`）
  - `runbook.params_files` を runbook YAML からの相対パスで解決し、列挙順マージ → `runbook.params` で上書き
  - 出力先を `<runbook>.parent.parent/dist/runbooks/<basename>.md` に固定
  - シナリオ関連ロジック（`SCENARIO_TEMPLATE`、`render_scenario`、scenario context）を全削除
- 旧 `examples/scenarios/0100-create-vpc.yaml` の `params:` を `examples/params/training-common.yaml` に移設
- `examples/runbooks/*.yaml` に `params_files: [../params/training-common.yaml]` を追記
- `templates/scenario.md.j2`、`examples/scenarios/`、`examples/dist/scenarios/` を削除
- 新CLIで生成し、`examples/dist/runbooks/{0101-create-vpc,0102-modify-dns-hostname}.md` が移行前のベースラインと `diff -u` でバイト単位完全一致することを確認

### 決定事項
- `params_files` のパス解決基準は runbook YAML ファイルの位置とする。CLI 実行ディレクトリには依存させない（複数の runbook を異なるディレクトリから指定された場合でも各 YAML 自身の位置から相対解決される）
- params YAML のフォーマットは「トップレベルに `params:` キーを置き、その下にフラットな key-value」で固定。マッピング以外を渡された場合は `ValueError` で停止する
- 複数 runbook 指定時のエラーは1件ずつ報告して残りを継続生成する。終了コードはファイル不在=2、テンプレ／YAML 不正=1、全件成功=0
- 旧 generate.py が出力していたシナリオ MD は廃止。手順書一覧の提示は将来 README 等のドキュメントで担う方針（SPEC §2 補足の通り）


## 2026-05-09: 仕様の簡素化（3層 → 2層、シングルリポジトリ化）

### 実施内容
- 仕様の簡素化方針を決定し、SPEC.md / TASKS.md を新仕様に合わせて全面的に書き直した
- 主な変更点：
  - シナリオ層を廃止し、構造を「手順書（Runbook）／スニペット（Snippet）」の2層に変更
  - 共通資産リポジトリ／プロジェクトリポジトリの分離を廃止し、`generate.py` と同居する単一リポジトリ構成に変更
  - テンプレート解決のオーバーライド機構を廃止（`generate.py` 隣接の `templates/`・`snippets/` のみ参照）
  - CLI を `python generate.py <runbook.yaml>...` の位置引数のみに簡素化（`--toolkit`／`--scenario` を廃止）
  - シナリオ共通パラメータの代替として、runbook YAML 側に `params_files: [...]` フィールドを導入
- `generate.py` 本体・`templates/scenario.md.j2`・`examples/scenarios/` の片付けは次ブランチで実施するため、TASKS.md フェーズ0 として切り出した

### 決定事項
- シナリオ層は廃止する。手順書一覧の提示は README 等のドキュメントで行い、ツールチェーンに上位層を持ち込まない。理由：
  - 運用上は手順書を1つずつ順に読みながら実行するだけで足り、シナリオMDの実利用価値が低かった
  - 上位層を持つほどパラメータ解決とテンプレート解決の経路が増え、仕組みの単純さを損なう
- 複数手順書で共有したいパラメータは `params_files` 経由で runbook YAML から明示的に指定する。共有粒度（業務単位・環境単位）の選択は YAML を書く側に委ねる
- ツールキットとプロジェクトを分離しない。1リポジトリに同居させ、業務が増えたら `examples/` の兄弟ディレクトリとして並べる方針とする
- テンプレートのオーバーライドは持たない。修正したい場合は共通テンプレートそのものを変更するか、新規テンプレートを追加する
- 既存の生成物（`examples/dist/`）は次ブランチでの新CLI動作確認後に再生成する。それまでは現行のままコミットを残す


## 2026-05-09: 生成物 .md の dist/ 配下への分離

### 実施内容
- SPEC §3.2 のプロジェクト構造図を更新。生成物は `project_root/dist/{scenarios,runbooks}/` に scenarios/runbooks の構造をミラーして配置する方針に変更
- `generate.py` に `dist_output_path()` を追加し、出力先を `project_root/dist/<rel>` に変更（`mkdir -p` 相当の親ディレクトリ作成も実装）
- 既存生成物 `examples/{scenarios,runbooks}/*.md` を削除し、`examples/dist/` 配下に再生成して動作確認

### 決定事項
- 配置方式は「dist/ ミラー配置」を採用。理由：
  - 定義（YAML）と生成物（MD）が完全に分離される
  - scenarios/runbooks の相対構造を保つため、Navigation 等の相対リンクが定義側と同じ表記でそのまま機能する（scenario → runbook: `../runbooks/X.md`、runbook → runbook: `./X.md`）
- 生成物は引き続き git にコミットする（SPEC §3.4 の方針維持）


## 2026-05-09: ドキュメント矛盾の修正

### 実施内容
- CLAUDE.md のタスク管理ファイル名を実体に合わせて `TODOS.md` → `TASKS.md` に修正
- CLAUDE.md に LOGS.md の運用ルールを追記
- Jinjaテンプレートの拡張子を SPEC.md の規定どおり `.j2.txt` → `.j2` に揃えた

### 決定事項
- 作業ログの構成は「日付見出し → 実施内容 → 決定事項」で統一する


## 2026-05-09: 生成ツール (generate.py) の基本実装

### 実施内容
- `generate.py` を実装。シナリオYAMLを起点に手順書MDとシナリオサマリーMDを生成する
- シナリオMD用テンプレート `templates/scenario.md.j2` を新設
- 依存関係を `requirements.txt`（PyYAML, Jinja2）に固定。`.tool-versions` で Python 3.13.12 を固定
- VPC作成シナリオで動作確認：`examples/scenarios/0100-create-vpc.md` ほか2件の手順書MDを生成

### 決定事項
- テンプレート/スニペット解決は Jinja2 `FileSystemLoader([project_root, toolkit_root])` で実現。プロジェクト側を先に登録することで SPEC §3.3 のオーバーライド優先順位を自然に表現
- スニペットの include はテンプレートからの相対パス（`snippets/ec2/create-vpc.md`）で参照する。Loader の検索パス設計と整合
- パラメータ解決の context は `{ runbook, scenario, navigation, **merged_params }` の構造とし、テンプレートからは `{{ region }}` のように params をフラットに参照できるようにした
- `trim_blocks=True, lstrip_blocks=True` を採用。インラインの `{% endif %}` が行末に来ると直後の改行を消費する挙動が判明したため、シナリオテンプレートでは `{% set %}` で変数化して回避
- 生成物 `.md` は SPEC §3.4 に従い git にコミットする
- テンプレート側の既知課題（`vpc_id` 未定義、日本語タイトルからの `RUNBOOK_TITLE` 生成）は generate.py の責務外として TASKS.md に切り出した


## 2025-02-26: サンプルYAML作成

### 実施内容
- シナリオYAML作成: `examples/scenarios/0100-create-vpc.yaml`
- 手順書YAML作成: `examples/runbooks/0101-create-vpc.yaml`
- 手順書YAML作成: `examples/runbooks/0102-modify-dns-hostname.yaml`

### 決定事項
- `navigation`（次の手順書へのリンク）は手順書YAML側に配置した
- `cli_option`（CLIオプション名）と`attribute`（API属性名）を分離し、手順書固有paramsとして定義する方針とした（0102の例: `attribute: enableDnsHostnames`, `cli_option: enable-dns-hostnames`）


## 2025-02-26: スニペット・テンプレート作成

### 実施内容
- EC2/VPC関連のスニペット4件を作成
  - `snippets/ec2/create-vpc.md`
  - `snippets/ec2/describe-vpcs.md`
  - `snippets/ec2/describe-vpc-attribute.md`
  - `snippets/ec2/modify-vpc-attribute.md`
- 手順書テンプレート2件を作成
  - `templates/ec2-create-vpc.md.j2`
  - `templates/ec2-modify-vpc-attribute.md.j2`

### 決定事項
- スニペット内ではJinja2の複雑なフィルター変換を避け、テンプレート側から適切な値を渡す方針とした
  - 例: `modify-vpc-attribute`のCLIオプション名（`enable-dns-hostnames`）は`cli_option`として明示的に渡す
  - `attribute`（API名: `enableDnsHostnames`）と`cli_option`（CLI名: `enable-dns-hostnames`）の変換責任はテンプレート/YAML側に持たせる
- スニペットのincludeは主処理の実行コマンドと事後確認で使用し、事前確認やパラメータ準備などコンテキスト依存の部分はテンプレート内に直書きとした
  - 事前確認のdescribe-vpcsは`--query`付き簡易一覧など使い方が異なるため
  - VPC ID取得などの中間ステップはテンプレートの責務として直書き


## 2025-02-26: 初期設計

### 実施内容
- CLI手順書の課題分析とディスカッション
- 3層構造（シナリオ・手順書・スニペット）の設計決定
- ファイル構成の決定（共通資産リポジトリ / プロジェクトリポジトリの分離）
- YAML定義フォーマットの決定
- パラメータ解決順序の決定
- テンプレート形式の決定（Markdown + Jinja2）
- SPEC.md 作成・承認

### 決定事項
- 手順書の最終形はMarkdownで、CloudShellで対話的に実行する運用は変えない
- スニペットは純粋なコマンドテンプレート。役割はテンプレート側が制御する
- テンプレートはMarkdown + Jinja2。宣言的YAMLではなく、最終出力が見える形式を採用
- シナリオ側に共通パラメータを持ち、各手順書に注入する
- テンプレート解決はプロジェクト側優先、共通側フォールバック
- 生成物のMarkdownはgitにコミットする

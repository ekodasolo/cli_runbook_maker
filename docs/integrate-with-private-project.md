# 案件リポジトリとの統合ガイド

ツールキットを GitHub で公開しつつ、案件固有の手順書をクローズドな環境（CodeCommit 等）で管理するための構成と運用手順。


## 背景

| リポジトリ | ホスト | 内容 | 公開範囲 |
|---|---|---|---|
| ツールキット | GitHub | generate.py, templates/, snippets/ | 公開 |
| 案件リポジトリ | CodeCommit 等 | 案件固有の YAML, params, 生成物 | 非公開 |

ツールキット自体の開発は GitHub で行い、案件リポジトリはそれをアップストリームとして取り込む。案件の内容がツールキット側に漏れることはない。


## 方式: git subtree

ツールキットを案件リポジトリの `toolkit/` ディレクトリに取り込む。submodule と異なり、clone 時の追加手順が不要で CodeCommit との相性も良い。

### subtree と submodule の比較

| 観点 | subtree | submodule |
|---|---|---|
| clone | `git clone` だけで完結 | `git clone --recursive` が必要 |
| ファイルの実体 | リポジトリに含まれる | ポインタのみ。別途 fetch が必要 |
| CI/CD | 特別な設定不要 | `submodule init/update` が必要 |
| CodeCommit との相性 | 問題なし | submodule URL の到達性に注意 |


## ディレクトリ構成

```
[GitHub] cli-runbook-toolkit/
  generate.py
  templates/
  snippets/
  projects/_template/
  projects/example/

[CodeCommit] client-a-runbooks/
  toolkit/                    <-- subtree でツールキットを格納
    generate.py
    templates/
    snippets/
    projects/_template/
    projects/example/
  projects/
    client-a/                 <-- 案件固有
      params/
      runbooks/
      dist/runbooks/
```

ツールキットが `toolkit/` の中に閉じ込められ、案件固有のファイルは `projects/` 以下に配置される。変更する領域が物理的に分離されるため、更新時のコンフリクトが構造的に起きない。


## セットアップ手順

### 1. 案件リポジトリを作成する

```bash
mkdir client-a-runbooks && cd client-a-runbooks
git init
```

### 2. ツールキットを subtree として取り込む

```bash
git subtree add \
    --prefix=toolkit \
    https://github.com/<org>/cli-runbook-toolkit.git \
    develop \
    --squash
```

`--squash` により、ツールキット側のコミット履歴は 1 つにまとめられて取り込まれる。案件リポジトリの履歴がクリーンに保たれる。

### 3. 案件プロジェクトを作成する

```bash
cp -r toolkit/projects/_template projects/client-a
```

### 4. 初期コミットして CodeCommit に push する

```bash
git add projects/client-a/
git commit -m "Add: client-a プロジェクト初期構成"
git remote add origin <codecommit-url>
git push -u origin main
```


## 日常の作業フロー

### 手順書の作成

```bash
# パラメータを編集
vi projects/client-a/params/common.yaml

# 手順書 YAML を作成
vi projects/client-a/runbooks/0101-create-vpc.yaml

# 生成（toolkit/ 内の generate.py を使う）
python toolkit/generate.py projects/client-a/runbooks/*.yaml

# 生成物を確認してコミット
git add projects/client-a/
git commit -m "Add: VPC 作成手順書"
```

### ツールキットの更新を取り込む

```bash
# upstream の最新を取り込む
git subtree pull \
    --prefix=toolkit \
    https://github.com/<org>/cli-runbook-toolkit.git \
    develop \
    --squash

# テンプレートやスニペットの更新が手順書に影響する場合は再生成
python toolkit/generate.py projects/client-a/runbooks/*.yaml

# 差分を確認してコミット
git diff projects/client-a/dist/
git add -A
git commit -m "update: toolkit 更新に伴う手順書再生成"
```


## generate.py がそのまま動く理由

generate.py のパス解決はすべて相対ベースで設計されている。

| 対象 | 解決方法 | subtree 配置での結果 |
|---|---|---|
| テンプレート | `Path(__file__).parent / 'templates/'` | `toolkit/templates/` |
| スニペット | 同上の FileSystemLoader | `toolkit/snippets/` |
| params_files | runbook YAML からの相対パス | `projects/client-a/params/` |
| dist 出力 | runbook YAML の `parent.parent/dist/runbooks/` | `projects/client-a/dist/runbooks/` |

`toolkit/` 内のコードを変更する必要はない。


## 守るべきルール

| ルール | 理由 |
|---|---|
| 案件リポジトリで `toolkit/` 内を直接編集しない | 次回の subtree pull でコンフリクトする |
| ツールキットの変更は GitHub 側で PR → merge | 変更がすべての案件に波及するため、レビューを経る |
| 案件固有のファイルは `projects/<name>/` 以下に置く | toolkit/ との境界を維持する |

スニペットやテンプレートの修正が必要な場合は、ツールキットリポジトリに PR を出し、merge 後に案件リポジトリ側で `git subtree pull` する。


## 案件が増えた場合

案件ごとに CodeCommit リポジトリを作り、同じ手順を繰り返す。

```bash
# 別案件
mkdir client-b-runbooks && cd client-b-runbooks
git init
git subtree add --prefix=toolkit <toolkit-url> develop --squash
cp -r toolkit/projects/_template projects/client-b
```

各案件リポジトリは独立しているため、互いの内容が漏れることはない。ツールキットの更新タイミングも案件ごとに制御できる。


## プロジェクト作成の補助スクリプト（任意）

案件リポジトリのルートに薄いラッパーを置くと便利:

```bash
#!/usr/bin/env bash
# new_project.sh（案件リポジトリ用）
set -euo pipefail
[ $# -ne 1 ] && { echo "Usage: $0 <project-name>" >&2; exit 1; }
TARGET="projects/$1"
[ -d "$TARGET" ] && { echo "Error: $TARGET already exists." >&2; exit 1; }
cp -r toolkit/projects/_template "$TARGET"
echo "Created: $TARGET/"
```

#!/usr/bin/env python3
"""AWS CLI 作業手順書ジェネレータ。

1つ以上の手順書 YAML を読み込み、共通の Jinja2 テンプレート
(``templates/runbook.md.j2``) と ``snippets/`` 配下のスニペットを使って
Markdown を生成する。テンプレート・スニペットはこのスクリプトと同じ
リポジトリの隣接ディレクトリに置く。共通資産（テンプレート・スニペッ
ト）と業務ごとの YAML は意図的に同一リポジトリに同居させる構成
（SPEC §3）。

使い方:
    python generate.py path/to/runbook.yaml [path...]

出力先:
    ``<project>/runbooks/<basename>.yaml`` は
    ``<project>/dist/runbooks/<basename>.md`` に出力される。
    ``<project>`` は ``runbooks/`` ディレクトリの親ディレクトリ
    （SPEC §7.2）。

このスクリプトの挙動は SPEC の以下の節に従う:
    - §3   ディレクトリ配置・資産の所在
    - §4.1 手順書 YAML スキーマ
    - §5   パラメータのマージ順序（params_files → runbook.params）
    - §6   テンプレート／スニペット規約
    - §7   CLI と出力先のマッピング
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


# Jinja2 の FileSystemLoader が検索するルート。テンプレート・スニペット
# はこのディレクトリからの相対パス（例: "templates/runbook.md.j2",
# "snippets/ec2/<x>.md"）で参照される。設計上固定で、CLI フラグ等から
# 変更する手段は持たない（SPEC §3.2）。
ASSETS_ROOT = Path(__file__).resolve().parent


def load_yaml(path: Path) -> dict[str, Any]:
    """YAML ファイルを dict として読み込む。空ファイルは ``{}`` を返す。"""
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _shell_var(name: object) -> str:
    """Jinja2 フィルタ: シェル変数参照を組み立てる。

    例: ``{{ "AWS_REGION" | shell_var }}`` -> ``${AWS_REGION}``

    ``templates/runbook.md.j2`` の §1.1（``cat << ETX`` で `shell_vars`
    を確認するブロック）から使われる。
    """
    return "${" + str(name) + "}"


def build_env() -> Environment:
    """Jinja2 環境を構築して返す。

    各設定の目的:
      - ``FileSystemLoader(ASSETS_ROOT)``:
        テンプレート・スニペットをリポジトリ相対パスで参照する
        （SPEC §6.3）。
      - ``trim_blocks`` + ``lstrip_blocks``:
        ``{% ... %}`` だけの行が出力に空行を残さないようにする。
        ``templates/runbook.md.j2`` の整形（SPEC §9 のセクション
        構造を保つ）にこの動作が前提となっている。
      - ``keep_trailing_newline``:
        テンプレート・スニペットの末尾改行を保持する。生成 Markdown
        が ``\\n`` で終わるようにするため。
      - ``shell_var`` フィルタ:
        詳細は ``_shell_var`` を参照。
    """
    env = Environment(
        loader=FileSystemLoader(str(ASSETS_ROOT)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["shell_var"] = _shell_var
    return env


def load_params_files(runbook_yaml_path: Path, params_files: list[str]) -> dict[str, Any]:
    """runbook YAML から参照される ``params_files`` を読み込みマージする。

    パスは runbook YAML 自身からの相対で解決する（cwd 非依存）。
    どのディレクトリから生成コマンドを叩いても同じ結果になる。

    マージ順は SPEC §5.1 のとおり「記述順、後勝ち」。本関数の戻り値
    に対して、呼び出し側が ``runbook.params`` を後から重ねることで
    最終的な解決値が決まる（``runbook.params`` が最優先）。

    各 params ファイルはトップレベルに ``params:`` マッピングを
    持つことを必須とする。それ以外の構造は誤用とみなしてエラーを
    早期に投げる。
    """
    merged: dict[str, Any] = {}
    base_dir = runbook_yaml_path.parent
    for rel in params_files:
        params_path = (base_dir / rel).resolve()
        if not params_path.exists():
            raise FileNotFoundError(
                f"params file not found: {params_path} "
                f"(referenced by {runbook_yaml_path.name})"
            )
        data = load_yaml(params_path)
        params = data.get("params") or {}
        if not isinstance(params, dict):
            raise ValueError(
                f"params file must have a top-level 'params:' mapping: {params_path}"
            )
        merged.update(params)
    return merged


def dist_output_path(runbook_yaml_path: Path) -> Path:
    """runbook YAML から生成物 Markdown のパスを算出する。

    SPEC §7.2 の規約:

        <project>/runbooks/<basename>.yaml
            -> <project>/dist/runbooks/<basename>.md

    ``<project>`` は YAML が置かれたディレクトリ（``runbooks/``）の
    さらに親ディレクトリと推論する。すなわち runbook YAML は
    ``<project>/runbooks/`` 直下に置くことが前提。
    """
    project_root = runbook_yaml_path.parent.parent
    basename = runbook_yaml_path.stem
    return project_root / "dist" / "runbooks" / f"{basename}.md"


def render_runbook(runbook_yaml_path: Path, env: Environment) -> Path:
    """runbook YAML を1件レンダリングし、生成物のパスを返す。

    処理の流れ:
      1. YAML を読み込み、必須フィールド（``runbook.template``）を検証。
      2. ``params_files`` をマージし、最後に ``runbook.params`` を上書き。
      3. ``runbook.template`` をテンプレート名として ``templates/`` 配下
         から解決する。
      4. Jinja2 のコンテキストを構築する。``params`` を dict として
         渡すと同時に、トップレベルにもフラットに展開する（前者は
         テンプレートの ``shell_vars`` 経由の間接参照、後者はスニペット
         からの直接参照に使われる。SPEC §6.6）。
      5. ``dist/runbooks/`` を必要に応じて作成し、生成物を書き込む。

    スキーマ違反は ``ValueError``、参照ファイル欠落は
    ``FileNotFoundError`` として呼び出し側に返す（``main()`` 側で
    集約して終了コードに反映する）。
    """
    # --- 1. 読み込みと検証 ---
    data = load_yaml(runbook_yaml_path)
    if "runbook" not in data:
        raise ValueError(
            f"runbook YAML must have a top-level 'runbook:' key: {runbook_yaml_path}"
        )
    runbook = data["runbook"]

    template_name = runbook.get("template")
    if not template_name:
        raise ValueError(
            f"runbook.template is required: {runbook_yaml_path}"
        )

    # --- 2. パラメータマージ: params_files をベースに runbook.params で上書き ---
    params_files = runbook.get("params_files") or []
    runbook_params = runbook.get("params") or {}
    merged_params = {
        **load_params_files(runbook_yaml_path, params_files),
        **runbook_params,
    }

    # --- 3. テンプレート解決 ---
    # YAML には短縮名（例: "runbook"）で書く。実体は
    # ``templates/<name>.md.j2`` を ASSETS_ROOT 配下から引く。
    template_path = f"templates/{template_name}.md.j2"
    try:
        template = env.get_template(template_path)
    except TemplateNotFound as e:
        raise FileNotFoundError(
            f"template not found: {template_path} "
            f"(referenced by {runbook_yaml_path.name})"
        ) from e

    # --- 4. コンテキスト構築とレンダリング ---
    # ``params`` を dict として渡す: テンプレート側で
    # ``params[shell_var_key]`` のように ``runbook.shell_vars`` 由来の
    # キーで間接参照するために必要。
    # 同じ値をトップレベルにも展開する: スニペットの「結果の例」で
    # ``{{ vpc_cidr }}`` のように直接参照して例示出力をリアル化するため。
    # （SPEC §6.6 のスニペット内変数規約に対応）
    context = {
        "runbook": runbook,
        "navigation": runbook.get("navigation") or {},
        "params": merged_params,
        **merged_params,
    }
    output = template.render(**context)

    # --- 5. dist/ への書き出し ---
    out_path = dist_output_path(runbook_yaml_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")
    return out_path


def main(argv: list[str] | None = None) -> int:
    """CLI エントリポイント。

    終了コード:
      0  全件成功
      1  少なくとも1件で検証エラー／テンプレート解決エラーが発生
      2  少なくとも1件で指定されたパスが存在しなかった

    ファイル単位のエラーはその場で stderr に報告するが処理は継続する。
    1件のタイポで残り全部の生成を止めない設計。
    """
    parser = argparse.ArgumentParser(
        description="Generate AWS CLI runbooks from YAML.",
    )
    parser.add_argument(
        "runbooks",
        nargs="+",
        help="Path(s) to runbook YAML file(s).",
    )
    args = parser.parse_args(argv)

    env = build_env()
    exit_code = 0
    for raw in args.runbooks:
        runbook_yaml = Path(raw).resolve()
        if not runbook_yaml.exists():
            print(f"error: runbook not found: {runbook_yaml}", file=sys.stderr)
            exit_code = 2
            continue
        try:
            out_path = render_runbook(runbook_yaml, env)
        except (FileNotFoundError, ValueError) as e:
            print(f"error: {e}", file=sys.stderr)
            exit_code = 1
            continue
        # 生成パスは可能な限り cwd 相対で表示する（ターミナルでの
        # 視認性を優先）。cwd 配下でなければ絶対パスにフォールバック。
        try:
            display = out_path.relative_to(Path.cwd())
        except ValueError:
            display = out_path
        print(f"generated: {display}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

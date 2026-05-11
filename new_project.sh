#!/usr/bin/env bash
#
# 新規プロジェクトを作成する
#
# Usage:
#   ./new_project.sh <project-name>
#
# Example:
#   ./new_project.sh project-a
#   → projects/project-a/ が作成される

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="${SCRIPT_DIR}/projects/_template"
PROJECTS_DIR="${SCRIPT_DIR}/projects"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <project-name>" >&2
    exit 1
fi

PROJECT_NAME="$1"
TARGET_DIR="${PROJECTS_DIR}/${PROJECT_NAME}"

if [ -d "${TARGET_DIR}" ]; then
    echo "Error: ${TARGET_DIR} already exists." >&2
    exit 1
fi

if [ ! -d "${TEMPLATE_DIR}" ]; then
    echo "Error: Template directory not found: ${TEMPLATE_DIR}" >&2
    exit 1
fi

cp -r "${TEMPLATE_DIR}" "${TARGET_DIR}"

# .gitkeep は生成物が入れば不要になるので残しておく
echo "Created: ${TARGET_DIR}/"
echo ""
echo "Next steps:"
echo "  1. projects/${PROJECT_NAME}/params/common.yaml を編集する"
echo "  2. projects/${PROJECT_NAME}/runbooks/0101-sample-create.yaml を参考に手順書 YAML を作成する"
echo "  3. python generate.py projects/${PROJECT_NAME}/runbooks/*.yaml で生成する"

#!/bin/sh
# Verify that this distributable Skill contains its required local rule chain.
# POSIX tools only: no personal paths, source-project names, or rg dependency.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

require_file() {
  if [ ! -f "$ROOT/$1" ]; then
    echo "missing required Skill file: $1" >&2
    exit 1
  fi
}

require_text() {
  if ! grep -F -q -- "$2" "$ROOT/$1"; then
    echo "missing required marker: $1 :: $2" >&2
    exit 1
  fi
}

for file in \
  SKILL.md \
  README.md \
  requirements.txt \
  KNOWN-ISSUES.md \
  references/production-workflow.md \
  references/content-planning.md \
  references/daily-plan-template.md \
  references/layout-recipes.md \
  references/layout-contracts.md \
  references/layout-rules.md \
  references/text-rendering-rules.md \
  references/daily-self-check.md \
  references/black-gold-system.md \
  assets/template/render.html \
  assets/fonts/NotoSerifCJKsc-Bold.otf \
  assets/fonts/NotoSansCJKsc-Medium.otf \
  assets/fonts/LICENSES.md \
  assets/baseline/baseline-notes.md \
  assets/baseline/01-hero-approved.png \
  assets/baseline/poster-preview-approved.jpg \
  scripts/render_longform.py \
  scripts/verify-case-layout.py
do
  require_file "$file"
done

require_text SKILL.md "固定渲染命令"
require_text SKILL.md "Playwright Chromium"
require_text SKILL.md "配方选择索引"
require_text references/black-gold-system.md "固定 Token"
require_text references/black-gold-system.md "人物呈现"
require_text references/daily-plan-template.md "内容关系与配方选择"
require_text references/content-planning.md "阅读区签名"
require_text references/production-workflow.md "首帧固定为 1 项 ImageGen 语义主视觉"
require_text references/daily-self-check.md "高风险布局"
require_text references/layout-rules.md "高风险布局 Layout Manifest"
require_text references/layout-contracts.md "同类内容过量时的合法处理"

personal_root='/'"Users/"
if find "$ROOT" -type f ! -path "$ROOT/.git/*" -exec grep -n -F "$personal_root" {} \; | grep -q .; then
  echo "independent Skill contains a personal local path" >&2
  exit 1
fi

echo "verified: distributable black-gold Skill rule chain is self-contained"

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
  assets/fonts/NotoSansCJKsc-Regular.otf \
  assets/fonts/NotoSansCJKsc-Medium.otf \
  assets/fonts/LICENSES.md \
  assets/baseline/baseline-notes.md \
  assets/baseline/01-hero-approved.png \
  assets/baseline/poster-preview-approved.jpg \
  scripts/package_poster_html.py \
  scripts/create_case_plan.py \
  scripts/render_longform.py \
  scripts/export_layout_manifest.py \
  scripts/verify-case-layout.py
do
  require_file "$file"
done

require_text SKILL.md "固定渲染命令"
require_text SKILL.md "Playwright Chromium"
require_text SKILL.md "export_layout_manifest.py"
require_text SKILL.md "配方选择索引"
require_text references/black-gold-system.md "固定 Token"
require_text references/black-gold-system.md "人物与信息模块"
require_text references/daily-plan-template.md "内容与营销确认稿"
require_text references/content-planning.md "阅读区签名"
require_text references/production-workflow.md "mentor-portrait"
require_text references/daily-self-check.md "手机比例检查"
require_text references/text-rendering-rules.md "NotoSansCJKsc-Regular.otf"
require_text references/text-rendering-rules.md "data-chapter-label"
require_text references/text-rendering-rules.md "data-fullwidth-text-axis"
require_text references/text-rendering-rules.md "data-gold-keyword"
require_text references/text-rendering-rules.md "data-hero-surface"
require_text references/black-gold-system.md "一个活动/项目语境眉题"
require_text references/layout-rules.md "data-hero-cover"
require_text references/daily-plan-template.md "首帧语义与金色关键词"
require_text references/layout-rules.md "浏览器实测 Layout Manifest"
require_text references/layout-contracts.md "同类内容过量时的合法处理"

personal_root='/'"Users/"
if find "$ROOT" -type f ! -path "$ROOT/.git/*" ! -path "$ROOT/.venv/*" ! -path "$ROOT/cases/*" ! -path '*/__pycache__/*' -exec grep -n -F "$personal_root" {} \; | grep -q .; then
  echo "independent Skill contains a personal local path" >&2
  exit 1
fi

echo "verified: distributable black-gold Skill rule chain is self-contained"

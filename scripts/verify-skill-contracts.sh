#!/bin/sh
# Verifies that the installed black-gold Skill is self-contained and that its
# mandatory local rule chain is present. It intentionally does not score a case.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

require_file() {
  if [ ! -f "$ROOT/$1" ]; then
    echo "missing required Skill file: $1" >&2
    exit 1
  fi
}

require_text() {
  if ! rg -F -q "$2" "$ROOT/$1"; then
    echo "missing required marker: $1 :: $2" >&2
    exit 1
  fi
}

for file in \
  SKILL.md \
  references/production-workflow.md \
  references/content-planning.md \
  references/daily-plan-template.md \
  references/layout-recipes.md \
  references/layout-contracts.md \
  references/layout-rules.md \
  references/text-rendering-rules.md \
  references/daily-self-check.md \
  references/black-gold-system.md \
  assets/baseline/baseline-notes.md \
  assets/baseline/01-hero-approved.png \
  assets/baseline/poster-preview-approved.jpg
do
  require_file "$file"
done

require_text SKILL.md "日常读取路由"
require_text SKILL.md "配方选择索引"
require_text references/black-gold-system.md "固定 Token"
require_text references/black-gold-system.md "人物呈现"
require_text references/daily-plan-template.md "内容关系与配方选择"
require_text references/content-planning.md "阅读区签名"
require_text references/production-workflow.md "首帧固定为 1 项 ImageGen 语义主视觉"
require_text references/daily-self-check.md "高风险布局"
require_text references/layout-rules.md "高风险布局 Layout Manifest"

forbidden_root='/Users/lifafa/Documents/'"Collage"
if rg -n -F "$forbidden_root" "$ROOT"; then
  echo "independent Skill contains a source-project path" >&2
  exit 1
fi

echo "verified: independent black-gold Skill rule chain is self-contained"

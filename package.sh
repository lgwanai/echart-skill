#!/bin/bash

# 获取当前时间戳，格式：YYYYMMDD_HHMMSS
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
PACKAGE_NAME="echart-skill_${TIMESTAMP}.zip"
DIST_DIR="dist"

# 确保 dist 目录存在
mkdir -p "$DIST_DIR"

echo "开始打包 Echart Skill..."

# 执行打包命令
# -r 递归
# -q 静默模式
# -x 排除指定文件或目录
zip -r -q "$DIST_DIR/$PACKAGE_NAME" . \
    -x "idea.md" \
    -x "package.sh" \
    -x "workspace.db" \
    -x "dist/*" \
    -x "tmp/*" \
    -x "outputs/*" \
    -x "test/*" \
    -x "*.git*" \
    -x "config.txt" \
    -x "*.gitignore" \
    -x "*.skill" \
    -x "*.DS_Store"

echo "✅ 打包完成！"
echo "📦 输出文件: $DIST_DIR/$PACKAGE_NAME"

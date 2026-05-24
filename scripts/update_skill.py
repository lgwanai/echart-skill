#!/usr/bin/env python3
"""
echart-skill 更新脚本

功能：
1. Git pull 从 GitHub 拉取最新代码
2. 备份旧文件到 backup 目录（带日期压缩包）
"""

import os
import sys
import subprocess
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


REPO_URL = "https://github.com/lgwanai/echart-skill"
BACKUP_DIR = "backup"
EXCLUDE_DIRS = {".git", "backup", "dist", "tmp", "outputs", "__pycache__", "node_modules"}
EXCLUDE_FILES = {"workspace.db", "workspace.duckdb", ".DS_Store", "*.pyc", "*.log"}


def get_skill_root():
    """获取 skill 根目录"""
    script_dir = Path(__file__).parent.resolve()
    return script_dir.parent


def should_exclude(path: Path) -> bool:
    """检查路径是否应排除"""
    name = path.name
    if name in EXCLUDE_DIRS:
        return True
    for pattern in EXCLUDE_FILES:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


def create_backup(skill_root: Path) -> str:
    """创建备份压缩包"""
    backup_dir = skill_root / BACKUP_DIR
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"echart-skill_backup_{timestamp}.zip"
    backup_path = backup_dir / backup_name
    
    print(f"📦 创建备份: {backup_path}")
    
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_root):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]
            
            for file in files:
                file_path = root_path / file
                if not should_exclude(file_path):
                    arcname = str(file_path.relative_to(skill_root))
                    zf.write(file_path, arcname)
    
    size_mb = backup_path.stat().st_size / (1024 * 1024)
    print(f"✅ 备份完成: {backup_name} ({size_mb:.2f} MB)")
    
    return str(backup_path)


def git_pull(skill_root: Path) -> bool:
    """执行 git pull"""
    print("\n📥 拉取最新代码...")
    
    git_dir = skill_root / ".git"
    if not git_dir.exists():
        print("❌ 当前目录不是 git 仓库")
        return False
    
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=skill_root,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✅ 更新成功")
            if result.stdout:
                print(result.stdout.strip())
            return True
        else:
            print(f"❌ 更新失败: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 更新超时")
        return False
    except Exception as e:
        print(f"❌ 更新异常: {e}")
        return False


def main():
    """主函数"""
    skill_root = get_skill_root()
    print(f"📁 Skill 目录: {skill_root}")
    
    backup_path = create_backup(skill_root)
    
    success = git_pull(skill_root)
    
    if success:
        print("\n" + "="*50)
        print("🎉 echart-skill 更新完成!")
        print(f"📦 备份文件: {backup_path}")
        print("="*50)
        return 0
    else:
        print("\n" + "="*50)
        print("⚠️ 更新失败，已保留备份")
        print(f"📦 备份文件: {backup_path}")
        print("="*50)
        return 1


if __name__ == "__main__":
    sys.exit(main())
import os
import argparse
from datetime import datetime

def add_metric(metric_name: str, metric_description: str, file_path: str = "references/metrics.md"):
    """
    Appends a new metric definition to the specified markdown file.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, file_path)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Check if file exists, if not initialize it
    is_new = not os.path.exists(full_path)
    
    with open(full_path, "a", encoding="utf-8") as f:
        if is_new:
            f.write("# 数据统计口径 (Metrics Definitions)\n\n")
            f.write("此文件记录了项目中涉及的所有核心统计口径和业务指标定义，作为后续大模型生成 SQL 时的重要上下文参考。\n\n")
            f.write("---\n\n")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"## {metric_name}\n\n")
        f.write(f"**定义/描述**: {metric_description}\n\n")
        f.write(f"*- 记录时间: {timestamp}*\n\n")
        f.write("---\n\n")
        
    print(f"✅ 成功追加统计口径: {metric_name} 到 {file_path}")

def main():
    parser = argparse.ArgumentParser(description="管理和保存业务数据统计口径")
    parser.add_argument("--name", "-n", type=str, required=True, help="口径名称 (Metric Name)")
    parser.add_argument("--desc", "-d", type=str, required=True, help="口径描述和定义 (Metric Description/Definition)")
    parser.add_argument("--file", "-f", type=str, default="references/metrics.md", help="保存路径 (默认: references/metrics.md)")
    
    args = parser.parse_args()
    
    add_metric(args.name, args.desc, args.file)

if __name__ == "__main__":  # pragma: no cover
    main()

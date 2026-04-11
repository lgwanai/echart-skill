#!/usr/bin/env python3
"""
CLI tool for exporting charts, dashboards, and Gantt charts as standalone HTML files.

Commands:
    export-chart CONFIG      Export chart as standalone HTML
    export-dashboard CONFIG  Export dashboard as standalone HTML
    export-gantt CONFIG      Export Gantt chart as standalone HTML

Each command accepts a config file path and optional flags:
    --output, -o    Output HTML file path (default: generated from title)
    --theme         ECharts theme (default, dark)

Examples:
    %(prog)s export-chart chart_config.json
    %(prog)s export-dashboard dashboard.json --output report.html
    %(prog)s export-gantt tasks.json --title "Timeline" --theme dark
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import re

# Add parent directory to path for imports when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.chart_generator import export_standalone_chart
from scripts.dashboard_generator import export_standalone_dashboard
from scripts.gantt_chart import export_standalone_gantt
from logging_config import get_logger

logger = get_logger(__name__)


def sanitize_filename(text: str) -> str:
    """Convert text to a safe filename.
    
    Replaces spaces and special characters with underscores,
    removes non-alphanumeric characters (except underscores and hyphens).
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized filename-safe string
    """
    sanitized = re.sub(r'[^\w\-\u4e00-\u9fff]', '_', text)
    sanitized = re.sub(r'_+', '_', sanitized).strip('_')
    return sanitized or "export"


def generate_default_filename(title: str) -> str:
    """Generate default filename from title with timestamp.
    
    Format: {sanitized_title}_{YYYYMMDD_HHMMSS}.html
    
    Args:
        title: Chart/dashboard title
        
    Returns:
        Generated filename
    """
    sanitized_title = sanitize_filename(title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{sanitized_title}_{timestamp}.html"


def cmd_export_chart(args):
    """Handle export-chart command."""
    config_path = Path(args.config)
    
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
        sys.exit(1)
    
    title = config.get('title', 'chart')
    
    if args.output:
        output_path = args.output
    else:
        output_path = generate_default_filename(title)
    
    try:
        result = export_standalone_chart(config, output_path, theme=args.theme)
        print(f"Exported: {result}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_export_dashboard(args):
    """Handle export-dashboard command."""
    config_path = Path(args.config)
    
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
        sys.exit(1)
    
    title = config.get('title', 'dashboard')
    
    if args.output:
        output_path = args.output
    else:
        output_path = generate_default_filename(title)
    
    try:
        result = export_standalone_dashboard(str(config_path), output_path, theme=args.theme)
        print(f"Exported: {result}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_export_gantt(args):
    """Handle export-gantt command."""
    config_path = Path(args.config)
    
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
        sys.exit(1)
    
    title = config.get('title', 'gantt')
    
    if args.output:
        output_path = args.output
    else:
        output_path = generate_default_filename(title)
    
    try:
        result = export_standalone_gantt(config, output_path, theme=args.theme)
        print(f"Exported: {result}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='chart-cli',
        description='Export charts, dashboards, and Gantt charts as standalone HTML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s export-chart chart_config.json
  %(prog)s export-dashboard dashboard.json --output report.html
  %(prog)s export-gantt tasks.json --title "Project Timeline" --theme dark
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # export-chart subcommand
    parser_chart = subparsers.add_parser('export-chart', help='Export chart as standalone HTML')
    parser_chart.add_argument('config', help='Path to chart configuration JSON file')
    parser_chart.add_argument('--output', '-o', help='Output HTML file path (default: generated from title)')
    parser_chart.add_argument('--theme', choices=['default', 'dark'], default='default',
                              help='ECharts theme (default: default)')
    parser_chart.set_defaults(func=cmd_export_chart)
    
    # export-dashboard subcommand
    parser_dashboard = subparsers.add_parser('export-dashboard', help='Export dashboard as standalone HTML')
    parser_dashboard.add_argument('config', help='Path to dashboard configuration JSON file')
    parser_dashboard.add_argument('--output', '-o', help='Output HTML file path (default: generated from title)')
    parser_dashboard.add_argument('--theme', choices=['default', 'dark'], default='default',
                                  help='ECharts theme (default: default)')
    parser_dashboard.set_defaults(func=cmd_export_dashboard)
    
    # export-gantt subcommand
    parser_gantt = subparsers.add_parser('export-gantt', help='Export Gantt chart as standalone HTML')
    parser_gantt.add_argument('config', help='Path to Gantt chart configuration JSON file')
    parser_gantt.add_argument('--output', '-o', help='Output HTML file path (default: generated from title)')
    parser_gantt.add_argument('--theme', choices=['default', 'dark'], default='default',
                              help='ECharts theme (default: default)')
    parser_gantt.set_defaults(func=cmd_export_gantt)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(2)
    
    args.func(args)


if __name__ == '__main__':
    main()

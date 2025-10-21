#!/usr/bin/env python3
"""
Excel Explorer - Helper script for Claude to explore large Excel files efficiently

This script provides command-line tools for incremental data exploration without
loading entire files into memory.

Usage:
    python excel_explorer.py <command> [options]

Commands:
    sample-sheet       - Get random sample of rows from a sheet
    sample-column      - Get unique values from a column
    check-overlap      - Check value overlap between two columns (possibly different sheets)
    column-stats       - Get statistics for a column
    find-keys          - Identify potential key columns (high uniqueness)
    suggest-joins      - Suggest potential joins between sheets based on data
"""

import sys
import argparse
import pandas as pd
import json
from pathlib import Path


def sample_sheet(file_path, sheet_name, n_rows=100, offset=0):
    """Sample rows from a sheet."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=offset, nrows=n_rows, engine='openpyxl')
        print(f"✅ Sampled {len(df)} rows from sheet '{sheet_name}' (offset: {offset})")
        print("\nColumn names:", list(df.columns))
        print("\nFirst few rows:")
        print(df.head(10).to_string())
        return df
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def sample_column(file_path, sheet_name, column_name, n_rows=1000, unique_only=True):
    """Sample values from a specific column."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=n_rows, engine='openpyxl')

        if column_name not in df.columns:
            print(f"❌ Column '{column_name}' not found in sheet '{sheet_name}'", file=sys.stderr)
            print(f"Available columns: {list(df.columns)}", file=sys.stderr)
            sys.exit(1)

        values = df[column_name].dropna()

        if unique_only:
            values = values.unique()
            print(f"✅ Found {len(values)} unique values in column '{column_name}'")
        else:
            print(f"✅ Sampled {len(values)} values from column '{column_name}'")

        print("\nSample values (first 20):")
        for i, val in enumerate(values[:20]):
            print(f"  {i+1}. {val}")

        if len(values) > 20:
            print(f"\n... and {len(values) - 20} more")

        # Print some statistics
        print(f"\nStatistics:")
        print(f"  Total sampled: {len(values)}")
        print(f"  Data type: {values.dtype}")

        return values
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def check_overlap(file_path, sheet1, col1, sheet2, col2, n_rows=1000):
    """Check value overlap between two columns."""
    try:
        df1 = pd.read_excel(file_path, sheet_name=sheet1, nrows=n_rows, engine='openpyxl')
        df2 = pd.read_excel(file_path, sheet_name=sheet2, nrows=n_rows, engine='openpyxl')

        if col1 not in df1.columns:
            print(f"❌ Column '{col1}' not found in sheet '{sheet1}'", file=sys.stderr)
            sys.exit(1)

        if col2 not in df2.columns:
            print(f"❌ Column '{col2}' not found in sheet '{sheet2}'", file=sys.stderr)
            sys.exit(1)

        values1 = set(df1[col1].dropna())
        values2 = set(df2[col2].dropna())

        overlap = values1.intersection(values2)
        only_in_1 = values1 - values2
        only_in_2 = values2 - values1

        overlap_pct = (len(overlap) / len(values1) * 100) if values1 else 0

        print(f"✅ Overlap Analysis: {sheet1}.{col1} ↔ {sheet2}.{col2}")
        print(f"\n📊 Results:")
        print(f"  Values in {sheet1}.{col1}: {len(values1)}")
        print(f"  Values in {sheet2}.{col2}: {len(values2)}")
        print(f"  Common values: {len(overlap)} ({overlap_pct:.1f}%)")
        print(f"  Only in {sheet1}: {len(only_in_1)}")
        print(f"  Only in {sheet2}: {len(only_in_2)}")

        if overlap_pct > 50:
            print(f"\n💡 HIGH OVERLAP - Strong potential for join/relationship!")
        elif overlap_pct > 20:
            print(f"\n💡 MODERATE OVERLAP - Possible relationship")
        else:
            print(f"\n💡 LOW OVERLAP - Likely not related")

        if overlap and len(overlap) <= 10:
            print(f"\nCommon values: {list(overlap)}")

        return {
            'overlap_count': len(overlap),
            'overlap_pct': overlap_pct,
            'values1': len(values1),
            'values2': len(values2)
        }
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def column_stats(file_path, sheet_name, column_name, n_rows=5000):
    """Get statistics for a column."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=n_rows, engine='openpyxl')

        if column_name not in df.columns:
            print(f"❌ Column '{column_name}' not found", file=sys.stderr)
            sys.exit(1)

        col = df[column_name]

        print(f"✅ Statistics for {sheet_name}.{column_name}")
        print(f"\n📊 Basic Info:")
        print(f"  Total values: {len(col)}")
        print(f"  Non-null: {col.notna().sum()}")
        print(f"  Null: {col.isna().sum()}")
        print(f"  Unique values: {col.nunique()}")
        print(f"  Data type: {col.dtype}")

        # Numeric stats
        if pd.api.types.is_numeric_dtype(col):
            print(f"\n📈 Numeric Statistics:")
            print(f"  Mean: {col.mean():.2f}")
            print(f"  Median: {col.median():.2f}")
            print(f"  Std Dev: {col.std():.2f}")
            print(f"  Min: {col.min():.2f}")
            print(f"  Max: {col.max():.2f}")

        # Most common values
        print(f"\n🔝 Most Common Values:")
        value_counts = col.value_counts().head(10)
        for val, count in value_counts.items():
            print(f"  {val}: {count} times")

        # Uniqueness assessment
        uniqueness = col.nunique() / len(col) * 100
        print(f"\n🔑 Uniqueness: {uniqueness:.1f}%")
        if uniqueness > 90:
            print("  → Likely a PRIMARY KEY or unique identifier!")
        elif uniqueness > 50:
            print("  → Moderate uniqueness - could be a foreign key")
        else:
            print("  → Low uniqueness - likely a categorical/descriptive column")

        return {
            'unique_pct': uniqueness,
            'total': len(col),
            'unique': col.nunique()
        }
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def find_keys(file_path, sheet_name, n_rows=2000, uniqueness_threshold=80):
    """Identify potential key columns based on uniqueness."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=n_rows, engine='openpyxl')

        print(f"✅ Analyzing columns in '{sheet_name}' for potential keys...")
        print(f"   (Uniqueness threshold: {uniqueness_threshold}%)\n")

        potential_keys = []

        for col_name in df.columns:
            col = df[col_name]
            uniqueness = col.nunique() / len(col) * 100

            if uniqueness >= uniqueness_threshold:
                potential_keys.append({
                    'column': col_name,
                    'uniqueness': uniqueness,
                    'unique_count': col.nunique(),
                    'total_count': len(col),
                    'data_type': str(col.dtype)
                })

        if potential_keys:
            print(f"🔑 Found {len(potential_keys)} potential key columns:\n")
            for key_info in sorted(potential_keys, key=lambda x: x['uniqueness'], reverse=True):
                print(f"  📌 {key_info['column']}")
                print(f"     Uniqueness: {key_info['uniqueness']:.1f}%")
                print(f"     Unique values: {key_info['unique_count']} / {key_info['total_count']}")
                print(f"     Type: {key_info['data_type']}")
                print()
        else:
            print(f"⚠️  No columns with uniqueness >= {uniqueness_threshold}% found")

        return potential_keys
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def suggest_joins(file_path, n_rows=1000):
    """Suggest potential joins between sheets based on column names and data overlap."""
    try:
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        sheets = xls.sheet_names

        print(f"✅ Analyzing {len(sheets)} sheets for potential joins...\n")

        suggestions = []

        # Compare each pair of sheets
        for i, sheet1 in enumerate(sheets):
            for sheet2 in sheets[i+1:]:
                df1 = pd.read_excel(file_path, sheet_name=sheet1, nrows=n_rows, engine='openpyxl')
                df2 = pd.read_excel(file_path, sheet_name=sheet2, nrows=n_rows, engine='openpyxl')

                # Find columns with similar names
                for col1 in df1.columns:
                    for col2 in df2.columns:
                        # Check if column names are similar or same
                        if col1.lower() == col2.lower() or \
                           col1.lower() in col2.lower() or \
                           col2.lower() in col1.lower():

                            # Check data overlap
                            try:
                                values1 = set(df1[col1].dropna().astype(str))
                                values2 = set(df2[col2].dropna().astype(str))

                                if values1 and values2:
                                    overlap = values1.intersection(values2)
                                    overlap_pct = len(overlap) / min(len(values1), len(values2)) * 100

                                    if overlap_pct > 10:  # At least 10% overlap
                                        suggestions.append({
                                            'sheet1': sheet1,
                                            'col1': col1,
                                            'sheet2': sheet2,
                                            'col2': col2,
                                            'overlap_pct': overlap_pct,
                                            'overlap_count': len(overlap)
                                        })
                            except:
                                pass

        if suggestions:
            print(f"🔗 Found {len(suggestions)} potential join opportunities:\n")
            for sug in sorted(suggestions, key=lambda x: x['overlap_pct'], reverse=True):
                strength = "🟢 STRONG" if sug['overlap_pct'] > 50 else "🟡 MODERATE" if sug['overlap_pct'] > 25 else "🟠 WEAK"
                print(f"{strength}")
                print(f"  {sug['sheet1']}.{sug['col1']} ↔ {sug['sheet2']}.{sug['col2']}")
                print(f"  Overlap: {sug['overlap_pct']:.1f}% ({sug['overlap_count']} common values)")
                print()
        else:
            print("⚠️  No obvious join opportunities found")
            print("   Try using check-overlap command to manually test specific column pairs")

        return suggestions
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Excel Explorer - Efficiently explore large Excel files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # sample-sheet command
    parser_sample = subparsers.add_parser('sample-sheet', help='Sample rows from a sheet')
    parser_sample.add_argument('file', help='Path to Excel file')
    parser_sample.add_argument('sheet', help='Sheet name')
    parser_sample.add_argument('-n', '--nrows', type=int, default=100, help='Number of rows to sample')
    parser_sample.add_argument('-o', '--offset', type=int, default=0, help='Starting row offset')

    # sample-column command
    parser_col = subparsers.add_parser('sample-column', help='Sample values from a column')
    parser_col.add_argument('file', help='Path to Excel file')
    parser_col.add_argument('sheet', help='Sheet name')
    parser_col.add_argument('column', help='Column name')
    parser_col.add_argument('-n', '--nrows', type=int, default=1000, help='Number of rows to read')
    parser_col.add_argument('--all', action='store_true', help='Show all values, not just unique')

    # check-overlap command
    parser_overlap = subparsers.add_parser('check-overlap', help='Check value overlap between columns')
    parser_overlap.add_argument('file', help='Path to Excel file')
    parser_overlap.add_argument('sheet1', help='First sheet name')
    parser_overlap.add_argument('col1', help='First column name')
    parser_overlap.add_argument('sheet2', help='Second sheet name')
    parser_overlap.add_argument('col2', help='Second column name')
    parser_overlap.add_argument('-n', '--nrows', type=int, default=1000, help='Number of rows to read')

    # column-stats command
    parser_stats = subparsers.add_parser('column-stats', help='Get statistics for a column')
    parser_stats.add_argument('file', help='Path to Excel file')
    parser_stats.add_argument('sheet', help='Sheet name')
    parser_stats.add_argument('column', help='Column name')
    parser_stats.add_argument('-n', '--nrows', type=int, default=5000, help='Number of rows to analyze')

    # find-keys command
    parser_keys = subparsers.add_parser('find-keys', help='Find potential key columns')
    parser_keys.add_argument('file', help='Path to Excel file')
    parser_keys.add_argument('sheet', help='Sheet name')
    parser_keys.add_argument('-n', '--nrows', type=int, default=2000, help='Number of rows to analyze')
    parser_keys.add_argument('-t', '--threshold', type=float, default=80, help='Uniqueness threshold %%')

    # suggest-joins command
    parser_joins = subparsers.add_parser('suggest-joins', help='Suggest potential joins between sheets')
    parser_joins.add_argument('file', help='Path to Excel file')
    parser_joins.add_argument('-n', '--nrows', type=int, default=1000, help='Number of rows to analyze')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == 'sample-sheet':
        sample_sheet(args.file, args.sheet, args.nrows, args.offset)
    elif args.command == 'sample-column':
        sample_column(args.file, args.sheet, args.column, args.nrows, not args.all)
    elif args.command == 'check-overlap':
        check_overlap(args.file, args.sheet1, args.col1, args.sheet2, args.col2, args.nrows)
    elif args.command == 'column-stats':
        column_stats(args.file, args.sheet, args.column, args.nrows)
    elif args.command == 'find-keys':
        find_keys(args.file, args.sheet, args.nrows, args.threshold)
    elif args.command == 'suggest-joins':
        suggest_joins(args.file, args.nrows)


if __name__ == '__main__':
    main()

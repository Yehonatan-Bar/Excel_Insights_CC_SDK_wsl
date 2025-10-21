#!/usr/bin/env python3
"""
Fast Excel file combiner using pandas.
Combines multiple Excel files into a single workbook with multiple sheets.
"""

import os
from pathlib import Path
import pandas as pd

def combine_excel_files_fast(source_dir, output_file):
    """
    Combine all Excel files from source_dir into a single workbook.
    Uses pandas for fast processing.

    Args:
        source_dir: Directory containing the Excel files to combine
        output_file: Path to the output Excel file
    """
    # Get all Excel files from the source directory
    source_path = Path(source_dir)
    excel_files = sorted(source_path.glob('*.xlsx'))

    if not excel_files:
        print(f"No Excel files found in {source_dir}")
        return

    print(f"Found {len(excel_files)} Excel file(s) to combine:")
    print()

    # Create Excel writer object
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        sheet_count = 0

        for excel_file in excel_files:
            print(f"Processing: {excel_file.name}")

            try:
                # Read all sheets from the Excel file
                excel_data = pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')

                # Process each sheet
                for sheet_name, df in excel_data.items():
                    # Create a unique sheet name
                    base_name = excel_file.stem
                    if len(excel_data) == 1:
                        # If there's only one sheet, just use the filename
                        new_sheet_name = base_name[:31]
                    else:
                        # If multiple sheets, combine filename and sheet name
                        new_sheet_name = f"{base_name}_{sheet_name}"[:31]

                    # Make sure the sheet name is unique
                    counter = 1
                    original_name = new_sheet_name
                    while new_sheet_name in writer.sheets:
                        new_sheet_name = f"{original_name[:28]}_{counter}"
                        counter += 1

                    # Write the dataframe to the new sheet
                    df.to_excel(writer, sheet_name=new_sheet_name, index=False)
                    sheet_count += 1
                    print(f"  > Added sheet: '{new_sheet_name}' ({len(df)} rows x {len(df.columns)} columns)")

            except Exception as e:
                print(f"  X Error processing {excel_file.name}: {str(e)}")
                continue

        print()
        print(f"+ Successfully combined {len(excel_files)} file(s) into {sheet_count} sheet(s)")

    print()
    print(f"Output file created: {output_file}")
    print(f"Total sheets in output: {sheet_count}")

if __name__ == "__main__":
    # Define paths
    script_dir = Path(__file__).parent
    source_directory = script_dir / "sources"
    output_filename = script_dir / "Combined_Excel_Files.xlsx"

    print("=" * 60)
    print("Fast Excel Files Combiner (using pandas)")
    print("=" * 60)
    print(f"Source directory: {source_directory}")
    print(f"Output file: {output_filename}")
    print("=" * 60)
    print()

    # Combine the files
    combine_excel_files_fast(source_directory, output_filename)

    print()
    print("=" * 60)
    print("Process completed!")
    print("=" * 60)

#!/usr/bin/env python3
import argparse
import os
import sys
from typing import List, Optional
import pdfplumber
import pandas as pd



def validate_dependencies() -> None:
	missing: List[str] = []
	if pdfplumber is None:
		missing.append("pdfplumber")
	if 'pd' not in globals() or pd is None:
		missing.append("pandas")
	if missing:
		sys.stderr.write(
			"Missing dependencies: {}. Install with: pip install -r requirements.txt\n".format(
				", ".join(missing)
			))
		sys.exit(1)


def extract_tables_from_pdf(pdf_path: str, page_range: Optional[str] = None) -> List[pd.DataFrame]:
	"""Extract tables from a PDF file as a list of DataFrames.

	page_range examples:
	- None => all pages
	- "1" => only page 1
	- "1-3" => pages 1 to 3 inclusive
	- "1,3,5" => pages 1, 3, and 5
	"""
	assert pd is not None

	if not os.path.exists(pdf_path):
		raise FileNotFoundError(f"PDF not found: {pdf_path}")

	pages_to_read: Optional[List[int]] = None
	if page_range:
		pages_to_read = []
		for token in page_range.split(','):
			token = token.strip()
			if '-' in token:
				start_s, end_s = token.split('-', 1)
				start, end = int(start_s), int(end_s)
				pages_to_read.extend(list(range(start, end + 1)))
			else:
				pages_to_read.append(int(token))

	tables: List[pd.DataFrame] = []
	with pdfplumber.open(pdf_path) as pdf:
		for idx, page in enumerate(pdf.pages, start=1):
			if pages_to_read is not None and idx not in pages_to_read:
				continue
			# Try multiple table extraction strategies
			page_tables = []
			try:
				page_tables = page.extract_tables()
			except Exception:
				page_tables = []

			for table in page_tables or []:
				if not table:
					continue
				df = pd.DataFrame(table)
				# Heuristic: drop fully empty columns and rows
				df.replace("", pd.NA, inplace=True)
				df.dropna(axis=0, how='all', inplace=True)
				df.dropna(axis=1, how='all', inplace=True)
				if not df.empty:
					tables.append(df)

	return tables


def write_tables_to_csv(tables: List[pd.DataFrame], output: str, merge: bool) -> None:
	assert pd is not None
	os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
	if merge:
		# Concatenate with blank row separators to preserve per-table separation
		frames: List[pd.DataFrame] = []
		for i, df in enumerate(tables):
			frames.append(df)
			# Add a separator row between tables except after the last one
			if i < len(tables) - 1:
				frames.append(pd.DataFrame([[]]))
			merged = pd.concat(frames, ignore_index=True)
			merged.to_csv(output, index=False, header=False)
	else:
		base, ext = os.path.splitext(output)
		for i, df in enumerate(tables, start=1):
			outfile = f"{base}_table{i}{ext or '.csv'}"
			df.to_csv(outfile, index=False, header=False)


def main() -> None:
	parser = argparse.ArgumentParser(description="Extract tables from a PDF into CSV.")
	parser.add_argument("pdf", help="Path to the input PDF file")
	parser.add_argument("-o", "--output", default="output.csv", help="Output CSV path or prefix (for multiple files)")
	parser.add_argument("-p", "--pages", default=None, help="Pages to extract, e.g. '1', '1-3', '1,3,5'")
	parser.add_argument("-s", "--split", action="store_true", help="Write each detected table to a separate CSV file")
	args = parser.parse_args()

	validate_dependencies()

	tables = extract_tables_from_pdf(args.pdf, args.pages)
	if not tables:
		print("No tables found.")
		return

	write_tables_to_csv(tables, args.output, merge=not args.split)
	if args.split:
		print(f"Wrote {len(tables)} CSV files with prefix: {args.output}")
	else:
		print(f"Wrote merged CSV to: {args.output}")


if __name__ == "__main__":
	main()

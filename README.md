# PDF Tables to CSV Converter

A small Python CLI to extract tables from a PDF and write them to CSV.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

- Merge all detected tables into one CSV:

```bash
python pdf_to_csv_converter.py input.pdf -o output.csv
```

- Split each detected table into its own file:

```bash
python pdf_to_csv_converter.py input.pdf -o tables.csv --split
# Produces tables_table1.csv, tables_table2.csv, ...
```

- Limit to certain pages:

```bash
python pdf_to_csv_converter.py input.pdf -p 1-3 -o tables.csv
```

Notes:
- Headers are not inferred; output files have no headers.
- Table detection quality depends on the PDF; scanned PDFs may perform poorly.

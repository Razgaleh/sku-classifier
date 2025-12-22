# PDF to CSV Conversion Process

## Overview: 4 Main Steps

```
┌─────────────────────────────────────────────────────────────────┐
│                    PDF to CSV Conversion Process                 │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   STEP 1     │  Parse Command-Line Arguments
    │   INPUT      │  • PDF file path
    └──────┬───────┘  • Output CSV path/prefix
           │          • Page range (optional)
           │          • Split mode (optional)
           ▼
    ┌──────────────┐
    │   STEP 2     │  Validate Dependencies
    │   VALIDATE   │  • Check pdfplumber installed
    └──────┬───────┘  • Check pandas installed
           │          • Exit if missing
           ▼
    ┌──────────────┐
    │   STEP 3     │  Extract Tables from PDF
    │   EXTRACT    │  • Open PDF file
    └──────┬───────┘  • Parse page range
           │          • Iterate through pages
           │          • Extract tables per page
           │          • Clean empty rows/columns
           │          • Return list of DataFrames
           ▼
    ┌──────────────┐
    │   STEP 4     │  Write Tables to CSV
    │   EXPORT     │  • Create output directory
    └──────┬───────┘  • If merge: Combine all tables
           │          • If split: Write separate files
           │          • Save CSV file(s)
           ▼
    ┌──────────────┐
    │   OUTPUT     │  CSV File(s) Ready!
    └──────────────┘
```

---

## Slide 1: Title Slide
**PDF to CSV Converter**
*Extract tables from PDF documents into CSV format*

---

## Slide 2: Process Overview (4 Steps)

### The Conversion Process

1. **📥 INPUT** - Parse command-line arguments
2. **✅ VALIDATE** - Check dependencies
3. **🔍 EXTRACT** - Extract tables from PDF
4. **💾 EXPORT** - Write to CSV file(s)

---

## Slide 3: Step 1 - Input Parsing

**Parse Command-Line Arguments**

- **Required**: PDF file path
- **Optional**:
  - `-o, --output`: Output CSV path (default: `output.csv`)
  - `-p, --pages`: Page range (`"1"`, `"1-3"`, `"1,3,5"`)
  - `-s, --split`: Split each table into separate files

**Example:**
```bash
python pdf_to_csv_converter.py document.pdf -o result.csv -p 1-5
```

---

## Slide 4: Step 2 - Validation

**Validate Dependencies**

- Check if `pdfplumber` is installed
- Check if `pandas` is installed
- Exit with error message if missing

**Purpose**: Ensure required libraries are available before processing

---

## Slide 5: Step 3 - Table Extraction

**Extract Tables from PDF**

1. **Open PDF** using pdfplumber
2. **Parse page range** (if specified)
3. **Iterate through pages**:
   - Extract tables from each page
   - Handle extraction errors gracefully
4. **Clean data**:
   - Convert empty strings to NA
   - Remove fully empty rows
   - Remove fully empty columns
5. **Return** list of cleaned DataFrames

---

## Slide 6: Step 4 - CSV Export

**Write Tables to CSV**

**Two Modes:**

1. **Merge Mode** (default):
   - Combine all tables into one CSV
   - Add blank separator rows between tables
   - Single output file

2. **Split Mode** (`-s` flag):
   - Each table → separate CSV file
   - Naming: `output_table1.csv`, `output_table2.csv`, etc.
   - Multiple output files

---

## Slide 7: Visual Flow Diagram

```
PDF File
   │
   ▼
┌─────────────────┐
│  Parse Args     │ ← Command-line options
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validate       │ ← Check dependencies
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extract Tables │ ← pdfplumber extraction
│  • Open PDF     │
│  • Parse pages  │
│  • Extract      │
│  • Clean data   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Export CSV     │ ← pandas to_csv()
│  • Merge OR     │
│  • Split        │
└────────┬────────┘
         │
         ▼
    CSV File(s)
```

---

## Slide 8: Key Features

**Key Features:**

✅ **Flexible page selection** - Extract from specific pages or ranges  
✅ **Multiple table support** - Handles multiple tables per PDF  
✅ **Data cleaning** - Automatically removes empty rows/columns  
✅ **Two export modes** - Merge or split tables  
✅ **Error handling** - Graceful handling of extraction failures  
✅ **Command-line interface** - Easy to use and scriptable  

---

## Slide 9: Technical Stack

**Technologies Used:**

- **Python 3** - Programming language
- **pdfplumber** - PDF table extraction library
- **pandas** - Data manipulation and CSV export
- **argparse** - Command-line argument parsing

---

## Slide 10: Summary

**4-Step Process:**

1. **INPUT** → Parse arguments
2. **VALIDATE** → Check dependencies  
3. **EXTRACT** → Get tables from PDF
4. **EXPORT** → Save as CSV

**Result:** Clean, structured CSV data from PDF tables


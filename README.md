# SKU Classifier Agent

An intelligent agent that automatically classifies SKU (Stock Keeping Unit) parts as either **HARDWARE** or **SOFTWARE** using Large Language Models (LLMs) and web search capabilities.

## Overview

The SKU Classifier Agent is a LangGraph-based system that processes product information (part numbers, descriptions, and segments) and classifies them into hardware or software categories. It leverages Ollama's Llama 3.1 model with web search integration via Brave Search API to make informed classification decisions.

## Features

- 🤖 **AI-Powered Classification**: Uses Llama 3.1 (8B) model for intelligent part classification
- 🔍 **Web Search Integration**: Automatically searches the web when additional product information is needed
- 📊 **Batch Processing**: Process entire CSV files or test on sample data
- 📈 **Evaluation Metrics**: Built-in evaluation script with accuracy, precision, recall, and F1-score
- 🔄 **Fallback Logic**: Keyword-based fallback classification if LLM fails
- 📁 **CSV Support**: Easy import/export of classification results
- 🎯 **Multi-GPU Support**: Configured for parallel processing with multiple GPUs

## Project Structure

```
sku/
├── data/                    # All data files (CSV, PDF, images)
│   ├── raw_data.csv
│   ├── dataset.csv
│   ├── dataset_classified.csv
│   ├── dataset_classified_ground_truth_labeled.csv
│   ├── palo_price_list.pdf
│   └── graph_diagram.png
├── src/                     # All source code
│   ├── sku_classifier_agent.py      # Main classifier
│   ├── clean_raw_data.py            # Data cleaning script
│   ├── pdf_to_csv_converter.py      # PDF extraction tool
│   ├── evaluate.py                  # Evaluation script
│   └── PDF_to_CSV_Process.md        # PDF conversion docs
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore patterns
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Architecture

The system uses **LangGraph** to create a stateful agent workflow:

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐
│  Chatbot    │◄────►│   Tools     │
│   (LLM)     │      │(Web Search) │
└──────┬──────┘      └─────────────┘
       │
       ▼
┌─────────────┐
│     END     │
└─────────────┘
```

The agent:
1. Receives product information (part number, segment, description)
2. Uses the LLM to analyze and classify the product
3. Optionally performs web searches for additional context
4. Returns classification: **HARDWARE** or **SOFTWARE**

## Installation

### Prerequisites

- Python 3.8+
- CUDA-capable GPUs (optional, for GPU acceleration)
- Ollama installed and running with Llama 3.1:8b model

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Razgaleh/sku-classifier
   cd sku-classifier
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and setup Ollama**:
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Pull the required model
   ollama pull llama3.1:8b
   ```

4. **Set up environment variables**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your API keys
   nano .env
   ```

   Required API keys:
   - **LangSmith API Key**: Get from [LangSmith](https://smith.langchain.com/) (optional, for tracing)
   - **Brave Search API Key**: Get from [Brave Search API](https://brave.com/search/api/) (required for web search)

## Configuration

The system is configured in `src/sku_classifier_agent.py`:

- **GPU Configuration**: Uses GPUs 0 and 1 by default (modify `CUDA_VISIBLE_DEVICES` if needed)
- **Model**: Llama 3.1:8b (change `model='llama3.1:8b'` to use a different model)
- **Context Window**: 4096 tokens
- **Batch Size**: 512

## Usage

### Main Classifier

Run the main classifier agent from the `src/` directory:

```bash
cd src
python sku_classifier_agent.py
```

You'll be prompted to:
1. **Test classification** on a sample of rows (option 1)
2. **Process full CSV file** for classification (option 2)

**Example workflow:**
```
SKU Classifier Agent
===================
1. Test classification on sample data
2. Process CSV file for classification

Enter your choice (1-2): 1
Enter CSV file path (default: ../data/dataset.csv): 
How many rows do you want to process? (Enter a number): 50
```

### Data Processing Pipeline

#### 1. Extract Data from PDF

Convert PDF price list to CSV:

```bash
cd src
python pdf_to_csv_converter.py ../data/palo_price_list.pdf -o ../data/raw_data.csv
```

Options:
- `-o, --output`: Output CSV path (default: `../data/raw_data.csv`)
- `-p, --pages`: Pages to extract, e.g., '1', '1-3', '1,3,5'
- `-s, --split`: Write each table to a separate CSV file

#### 2. Clean Raw Data

Prepare your raw data for classification:

```bash
cd src
python clean_raw_data.py
```

This script:
- Reads `../data/raw_data.csv`
- Sets column names: `PART_NUMBER`, `PART_SEG`, `PART_DESCRIPTION`, `PART_CATEGORY`
- Sets all `PART_SEG` values to 'PALO'
- Removes price column
- Outputs to `../data/dataset.csv`

**Input format** (`raw_data.csv`):
```
PART_SEG, PART_NUMBER, PART_DESCRIPTION, PART_PRICE
```

**Output format** (`dataset.csv`):
```
PART_NUMBER, PART_SEG, PART_DESCRIPTION, PART_CATEGORY
```

#### 3. Run Classification

Process the cleaned dataset:

```bash
cd src
python sku_classifier_agent.py
```

Select option 2 to process the full dataset.

#### 4. Evaluate Results

Evaluate classification accuracy against ground truth:

```bash
cd src
python evaluate.py
```

This script:
- Loads `../data/dataset_classified_ground_truth_labeled.csv`
- Compares `PART_CATEGORY` (predictions) with `GROUND_TRUTH`
- Calculates accuracy, precision, recall, F1-score
- Displays confusion matrix
- Shows misclassifications and rows with missing ground truth

**Expected CSV format** for evaluation:
```
PART_NUMBER, PART_SEG, PART_DESCRIPTION, PART_CATEGORY, GROUND_TRUTH
```

## Classification Rules

The agent classifies products based on these rules:

### HARDWARE
- Physical devices and appliances
- Hardware components
- Physical security appliances
- Network devices
- Servers and storage devices
- Physical equipment

### SOFTWARE
- Software licenses and subscriptions
- Digital products
- Virtual appliances
- Software-only solutions
- Cloud services
- Digital downloads

## Output

The classifier generates a CSV file with an additional `PART_CATEGORY` column:

**Input** (`dataset.csv`):
```csv
PART_NUMBER,PART_SEG,PART_DESCRIPTION,PART_CATEGORY
PA-220,PALO,Palo Alto Networks PA-220 Hardware Appliance,
```

**Output** (`dataset_classified.csv`):
```csv
PART_NUMBER,PART_SEG,PART_DESCRIPTION,PART_CATEGORY
PA-220,PALO,Palo Alto Networks PA-220 Hardware Appliance,HARDWARE
```

## Evaluation Metrics

The evaluation script provides:

- **Accuracy**: Overall classification accuracy
- **Precision**: Macro-averaged precision across classes
- **Recall**: Macro-averaged recall across classes
- **F1-Score**: Macro-averaged F1-score
- **Confusion Matrix**: Detailed breakdown of predictions vs. ground truth
- **Misclassification Report**: List of incorrectly classified items

## Troubleshooting

### Common Issues

1. **Ollama not found**:
   - Ensure Ollama is installed and running: `ollama serve`
   - Verify model is available: `ollama list`

2. **CUDA/GPU errors**:
   - If you don't have GPUs, modify `CUDA_VISIBLE_DEVICES` in the script
   - Set `num_gpu: 0` in the LLM options for CPU-only mode

3. **API Key errors**:
   - Verify environment variables are set: `echo $BRAVE_SEARCH_API_KEY`
   - LangSmith API key is optional but recommended for debugging

4. **Import errors**:
   - Install all dependencies: `pip install -r requirements.txt`
   - Ensure you're using Python 3.8+

5. **Path errors**:
   - Make sure you're running scripts from the `src/` directory
   - Or use absolute paths when specifying file locations

## Dependencies

- `langgraph` - Agent workflow framework
- `langchain-ollama` - Ollama LLM integration
- `langchain-community` - Community tools (Brave Search)
- `langsmith` - Tracing and monitoring (optional)
- `pandas` - Data manipulation
- `scikit-learn` - Evaluation metrics
- `pdfplumber` - PDF processing

See `requirements.txt` for version details.



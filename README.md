# SKU Classifier Agent

An intelligent agent that automatically classifies SKU (Stock Keeping Unit) parts as either **HARDWARE** or **SOFTWARE** using Large Language Models (LLMs) and web search capabilities.

## Overview

The SKU Classifier Agent is a LangGraph-based system that processes product information (part numbers, descriptions, and segments) and classifies them into hardware or software categories. It leverages NVIDIA NIM (NVIDIA Inference Microservices) running Meta's Llama 3.1 8B Instruct model locally with web search integration via Brave Search API to make informed classification decisions.

## Features

- 🤖 **AI-Powered Classification**: Uses Meta's Llama 3.1 8B Instruct model via NVIDIA NIM for intelligent part classification
- 🚀 **Local NVIDIA NIM Deployment**: Run inference locally with optimized NVIDIA microservices
- 🔍 **Web Search Integration**: Automatically searches the web when additional product information is needed
- 📊 **Batch Processing**: Process entire CSV files or test on sample data
- 📈 **Evaluation Metrics**: Built-in evaluation script with accuracy, precision, recall, and F1-score
- 🔄 **Fallback Logic**: Keyword-based fallback classification if LLM fails
- 📁 **CSV Support**: Easy import/export of classification results
- ⚡ **High-Performance Inference**: Optimized for low latency and high throughput with NVIDIA hardware

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

### Why NVIDIA NIM?

NVIDIA NIM (NVIDIA Inference Microservices) provides several advantages for production deployment:

- **Optimized Performance**: Pre-built containers optimized for NVIDIA GPUs with TensorRT-LLM
- **Easy Deployment**: Deploy locally or in the cloud with a single Docker command
- **Enterprise-Ready**: Production-grade inference with built-in monitoring and scaling
- **Compatibility**: Works with LangChain and other popular frameworks
- **Flexibility**: Switch between local deployment and cloud API with minimal code changes
- **Cost-Effective**: Run inference locally to reduce API costs for high-volume workloads

## Installation

### Prerequisites

- Python 3.8+
- CUDA-capable NVIDIA GPU (recommended for optimal performance)
- Docker (for running NVIDIA NIM container)
- NVIDIA Container Toolkit (for GPU access in Docker)
- NVIDIA API Key (get from [NVIDIA AI](https://build.nvidia.com/))

### Setup

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   git clone https://github.com/Razgaleh/sku-classifier
   cd sku-classifier
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up NVIDIA NIM (Local Deployment)**:
   
   Pull and run the NVIDIA NIM container with Llama 3.1 8B Instruct model:
   
   ```bash
   # Login to NVIDIA NGC (you'll need an NGC API key)
   docker login nvcr.io
   
   # Pull the NIM container for Llama 3.1 8B Instruct
   docker pull nvcr.io/nim/meta/llama-3.1-8b-instruct:latest
   
   # Run the NIM container (exposing port 8000)
   docker run -d \
     --gpus all \
     --shm-size=16GB \
     -e NGC_API_KEY=$NGC_API_KEY \
     -v "$HOME/.cache/nim:/opt/nim/.cache" \
     -p 8000:8000 \
     nvcr.io/nim/meta/llama-3.1-8b-instruct:latest
   ```
   
   The NIM service will be available at `http://localhost:8000/v1`

4. **Set up environment variables**:
   Create a `.env` file or export the following environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your API keys
   nano .env
   ```

   - **NVIDIA API Key**: Get from [NVIDIA AI](https://build.nvidia.com/) (required for NIM authentication)
   - **LangSmith API Key**: Get from [LangSmith](https://smith.langchain.com/) (optional, for tracing)
   - **Brave Search API Key**: Get from [Brave Search API](https://brave.com/search/api/) (required for web search)
   
   Example `.env` file:
   ```bash
   NVIDIA_API_KEY=your_nvidia_api_key_here
   LANGSMITH_API_KEY=your_langsmith_key_here
   BRAVE_SEARCH_API_KEY=your_brave_search_key_here
   ```

## Configuration

The system is configured in `src/sku_classifier_agent.py`:

- **NIM Endpoint**: Local deployment at `http://localhost:8000/v1` (lines 39-42)
- **Model**: `meta-llama/llama-3.1-8b-instruct` (change to use different NIM-supported models)
- **LLM Provider**: `ChatNVIDIA` from `langchain_nvidia_ai_endpoints`
- **Tools**: BraveSearch with count=3 results per query

To use NVIDIA's cloud API instead of local NIM:
```python
# Remove the base_url parameter to use cloud API
llm = ChatNVIDIA(
    model="meta-llama/llama-3.1-8b-instruct"
)
```

## Usage

### Main Classifier

Run the main classifier agent:

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

#### Clean Raw Data

Prepare your raw data CSV file:

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

Evaluate classification results against ground truth:

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

1. **NIM Container not running**:
   - Check if the container is running: `docker ps | grep nim`
   - View container logs: `docker logs <container_id>`
   - Ensure port 8000 is not already in use: `lsof -i :8000`
   - Restart the NIM container if needed

2. **Connection to NIM fails**:
   - Verify NIM is accessible: `curl http://localhost:8000/v1/health`
   - Check the base_url in `sku_classifier_agent.py` matches your NIM endpoint
   - Ensure firewall/network settings allow localhost connections

3. **CUDA/GPU errors**:
   - Verify NVIDIA drivers are installed: `nvidia-smi`
   - Ensure Docker has GPU access: `docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi`
   - Check NVIDIA Container Toolkit is installed properly

4. **API Key errors**:
   - Verify environment variables are set: `echo $NVIDIA_API_KEY`
   - Get your NVIDIA API key from [NVIDIA AI](https://build.nvidia.com/)
   - LangSmith API key is optional but recommended for debugging
   - Brave Search API key is required for web search functionality

5. **Import errors**:
   - Install all dependencies: `pip install -r requirements.txt`
   - Ensure you're using Python 3.8+
   - Try upgrading pip: `pip install --upgrade pip`

6. **Path errors**:
   - Make sure you're running scripts from the `src/` directory
   - Or use absolute paths when specifying file locations

7. **Model loading issues**:
   - Ensure sufficient disk space for model cache (~20GB)
   - Check Docker container has enough shared memory (--shm-size=16GB)
   - Verify model is compatible with your GPU's compute capability

## Dependencies

- `langgraph` - Agent workflow framework
- `langchain-nvidia-ai-endpoints` - NVIDIA NIM integration
- `langchain-community` - Community tools (Brave Search)
- `langsmith` - Tracing and monitoring (optional)
- `pandas` - Data manipulation
- `scikit-learn` - Evaluation metrics
- `pdfplumber` - PDF processing

See `requirements.txt` for version details.



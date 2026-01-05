import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Get the project root directory (parent of src/)
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

# Load the data
df = pd.read_csv(DATA_DIR / "dataset_classified_ground_truth_labeled.csv")

# Get the last two columns (PART_CATEGORY and GROUND_TRUTH)
predictions = df.iloc[:, -2].str.upper().str.strip()  # PART_CATEGORY
ground_truth = df.iloc[:, -1].str.upper().str.strip()  # GROUND_TRUTH

# Find rows with NULL/missing ground truth
null_mask = (ground_truth.isna()) | (ground_truth == '') | (ground_truth == 'NULL')
valid_mask = ~null_mask

# Calculate metrics only for valid rows
predictions_valid = predictions[valid_mask]
ground_truth_valid = ground_truth[valid_mask]

# Calculate metrics
accuracy = accuracy_score(ground_truth_valid, predictions_valid)
precision = precision_score(ground_truth_valid, predictions_valid, average='macro', zero_division=0)
recall = recall_score(ground_truth_valid, predictions_valid, average='macro', zero_division=0)
f1 = f1_score(ground_truth_valid, predictions_valid, average='macro', zero_division=0)
cm = confusion_matrix(ground_truth_valid, predictions_valid, labels=['HARDWARE', 'SOFTWARE'])

# Print results
print("=" * 50)
print("EVALUATION RESULTS")
print("=" * 50)
print(f"\nAccuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-Score: {f1:.4f}")
print(f"\nCorrect: {(predictions_valid == ground_truth_valid).sum()}/{len(predictions_valid)}")
print(f"Incorrect: {(predictions_valid != ground_truth_valid).sum()}/{len(predictions_valid)}")
print(f"Rows with NULL ground truth: {null_mask.sum()}")

print("\n" + "-" * 50)
print("Confusion Matrix:")
print("-" * 50)
print("                Predicted")
print("              HARDWARE  SOFTWARE")
print(f"Actual HARDWARE    {cm[0][0]:4d}      {cm[0][1]:4d}")
print(f"       SOFTWARE    {cm[1][0]:4d}      {cm[1][1]:4d}")

# Show misclassifications with row numbers
misclassified = df[valid_mask][predictions_valid != ground_truth_valid]
if len(misclassified) > 0:
    print(f"\nMisclassifications ({len(misclassified)}):")
    print("-" * 50)
    for idx, row in misclassified.iterrows():
        # idx is the pandas index (0-based), but we want CSV row number (1-based, +1 for header)
        row_num = idx + 2  # +1 for 0-based to 1-based, +1 for header row
        print(f"Row {row_num}: {row.iloc[0]} | Predicted: {row.iloc[-2]} → Actual: {row.iloc[-1]}")

# Show rows with NULL ground truth
if null_mask.sum() > 0:
    null_rows = df[null_mask]
    print(f"\nRows with NULL/Missing Ground Truth ({len(null_rows)}):")
    print("-" * 50)
    for idx, row in null_rows.iterrows():
        row_num = idx + 2  # +1 for 0-based to 1-based, +1 for header row
        part_num = row.iloc[0] if pd.notna(row.iloc[0]) else "(empty)"
        predicted = row.iloc[-2] if pd.notna(row.iloc[-2]) else "(empty)"
        print(f"Row {row_num}: {part_num} | Predicted: {predicted} | Ground Truth: NULL")
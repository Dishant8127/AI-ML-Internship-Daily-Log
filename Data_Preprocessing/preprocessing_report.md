
# Preprocessing Report

## Dataset Information
- Dataset Name: Disaster Tweets Dataset
- File Format: CSV
- Total Rows Processed: 11221

## Steps Performed

### 1. Data Collection
- Loaded dataset using pandas.
- Verified CSV file format.

### 2. Data Inspection
- Checked dataset shape.
- Verified column names and data types.
- Displayed sample rows.

### 3. Data Cleaning
- Removed duplicate tweets.
- Handled missing values.
- Removed irrelevant columns.

### 4. Text Preprocessing
- Converted text to lowercase.
- Removed URLs.
- Removed emojis.
- Removed special characters and numbers.
- Removed stop words.
- Applied tokenization.
- Applied lemmatization.

### 5. Final Validation
- Checked label distribution.
- Analyzed token length distribution.
- Removed token length outliers.

### 6. Output Files
- cleaned_data.csv
- cleaned_data.jsonl


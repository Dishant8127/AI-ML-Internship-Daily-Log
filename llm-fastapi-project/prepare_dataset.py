"""Dataset preparation for the AI Technical Support Assistant.

Rebuilds the fine-tuning dataset from the verified technical Q&A records used in
``Untitled8.ipynb`` (Day 1), then splits it 70% / 15% / 15% into
``data/train.jsonl``, ``data/validation.jsonl`` and ``data/test.jsonl``.

The split reproduces ``sklearn.model_selection.train_test_split(..., random_state=42)``
using numpy only, so the files can be regenerated without the Colab-only dependency.

Run from this directory:

    python prepare_dataset.py
"""

import json
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent / "data"


def train_test_split(items, test_size, random_state):
    """Minimal reimplementation of sklearn's shuffled train_test_split."""
    n_samples = len(items)
    n_test = int(np.ceil(test_size * n_samples))
    permutation = np.random.RandomState(random_state).permutation(n_samples)
    test_idx = permutation[:n_test]
    train_idx = permutation[n_test:]
    return [items[i] for i in train_idx], [items[i] for i in test_idx]


data = [
    # Python
    {"instruction": "What is a Python list?", "input": "",
     "output": "A list is an ordered, mutable collection that can store multiple items, including duplicate values."},
    {"instruction": "What is a Python tuple?", "input": "",
     "output": "A tuple is an ordered collection that cannot be modified after it is created."},
    {"instruction": "What is a Python dictionary?", "input": "",
     "output": "A dictionary stores key-value pairs. Keys must be unique and hashable."},
    {"instruction": "What is the difference between == and is in Python?", "input": "",
     "output": "The == operator compares values, while is checks whether two references point to the same object."},
    {"instruction": "What is a Python function?", "input": "",
     "output": "A function is a reusable block of code defined with def that can accept arguments and return a result."},
    {"instruction": "What is a Python decorator?", "input": "",
     "output": "A decorator wraps a function or class to extend or modify its behavior without directly changing its source code."},
    {"instruction": "What is exception handling in Python?", "input": "",
     "output": "Exception handling uses try and except blocks to handle runtime errors. A finally block can run cleanup code."},
    {"instruction": "What is a Python class?", "input": "",
     "output": "A class defines a structure for creating objects with attributes and methods."},
    {"instruction": "What is inheritance in Python?", "input": "",
     "output": "Inheritance allows a class to derive attributes and methods from another class."},
    {"instruction": "What is a Python generator?", "input": "",
     "output": "A generator produces values lazily, commonly using yield, instead of creating all results at once."},

    # APIs and HTTP
    {"instruction": "What is a REST API?", "input": "",
     "output": "A REST API exposes resources through HTTP and commonly uses methods such as GET, POST, PUT, PATCH, and DELETE."},
    {"instruction": "What is the difference between GET and POST?", "input": "",
     "output": "GET requests retrieve data. POST requests submit data for processing or resource creation."},
    {"instruction": "What does HTTP status code 200 mean?", "input": "",
     "output": "HTTP 200 OK indicates that the request succeeded."},
    {"instruction": "What does HTTP status code 404 mean?", "input": "",
     "output": "HTTP 404 Not Found indicates that the requested resource could not be found."},
    {"instruction": "What does HTTP status code 500 mean?", "input": "",
     "output": "HTTP 500 Internal Server Error indicates that the server encountered an unexpected condition."},
    {"instruction": "What is JSON?", "input": "",
     "output": "JSON is a text-based data format that represents structured data using objects, arrays, strings, numbers, booleans, and null."},
    {"instruction": "What is an API endpoint?", "input": "",
     "output": "An API endpoint is a specific URL and HTTP method through which a client accesses an API operation."},
    {"instruction": "What is FastAPI?", "input": "",
     "output": "FastAPI is a Python framework for building APIs with type hints, request validation, and automatic OpenAPI documentation."},
    {"instruction": "What is request validation?", "input": "",
     "output": "Request validation checks incoming data against expected types and rules before processing it."},
    {"instruction": "What is the difference between PUT and PATCH?", "input": "",
     "output": "PUT generally replaces a resource representation, while PATCH applies partial modifications to a resource."},

    # SQL and databases
    {"instruction": "What is SQL?", "input": "",
     "output": "SQL is a language used to query and manage data in relational database systems."},
    {"instruction": "What is a primary key?", "input": "",
     "output": "A primary key uniquely identifies each row in a table and cannot contain NULL values."},
    {"instruction": "What is a foreign key?", "input": "",
     "output": "A foreign key references a candidate key, usually a primary key, in the same or another table to enforce referential integrity."},
    {"instruction": "What is the difference between WHERE and HAVING?", "input": "",
     "output": "WHERE filters rows before grouping. HAVING filters groups after GROUP BY."},
    {"instruction": "What does GROUP BY do in SQL?", "input": "",
     "output": "GROUP BY groups rows with matching values so aggregate functions can calculate results for each group."},
    {"instruction": "What is an SQL JOIN?", "input": "",
     "output": "A JOIN combines rows from two or more tables using a related column or join condition."},
    {"instruction": "What is an INNER JOIN?", "input": "",
     "output": "An INNER JOIN returns rows that satisfy the join condition in both tables."},
    {"instruction": "What is a database index?", "input": "",
     "output": "An index can speed up data retrieval, but it requires storage and can add overhead to data modifications."},
    {"instruction": "What is database normalization?", "input": "",
     "output": "Normalization organizes relational data to reduce unnecessary duplication and improve data integrity."},
    {"instruction": "What is a SQL transaction?", "input": "",
     "output": "A transaction is a group of database operations treated as one logical unit, commonly governed by ACID properties."},

    # Machine learning and software
    {"instruction": "What is machine learning?", "input": "",
     "output": "Machine learning is a field of AI in which algorithms learn patterns from data to make predictions or decisions."},
    {"instruction": "What is supervised learning?", "input": "",
     "output": "Supervised learning trains a model using examples containing input features and target labels or values."},
    {"instruction": "What is overfitting?", "input": "",
     "output": "Overfitting occurs when a model learns training data too closely and performs poorly on unseen data."},
    {"instruction": "What is a train-test split?", "input": "",
     "output": "A train-test split separates data for model fitting from data reserved to evaluate performance on unseen examples."},
    {"instruction": "What is precision in machine learning?", "input": "",
     "output": "Precision is the proportion of predicted positive cases that are actually positive: TP divided by TP plus FP."},
    {"instruction": "What is recall in machine learning?", "input": "",
     "output": "Recall is the proportion of actual positive cases correctly identified: TP divided by TP plus FN."},
    {"instruction": "What is Git?", "input": "",
     "output": "Git is a distributed version control system that tracks changes to files and supports collaboration."},
    {"instruction": "What is Docker?", "input": "",
     "output": "Docker packages an application and its dependencies into containers to help it run consistently across environments."},
    {"instruction": "What is unit testing?", "input": "",
     "output": "Unit testing checks individual functions or components in isolation to verify their expected behavior."},
    {"instruction": "What is the difference between authentication and authorization?", "input": "",
     "output": "Authentication verifies who a user is. Authorization determines what that user is allowed to access or do."}
]

# Validate records
seen = set()
clean_data = []

for item in data:
    question = item["instruction"].strip()
    answer = item["output"].strip()

    if not question or not answer:
        continue

    key = question.casefold()
    if key in seen:
        continue

    seen.add(key)
    clean_data.append({
        "instruction": question,
        "input": item["input"].strip(),
        "output": answer
    })

# Split: 70% train, 15% validation, 15% test
train_data, remaining = train_test_split(clean_data, test_size=0.30, random_state=42)
val_data, test_data = train_test_split(remaining, test_size=0.50, random_state=42)

# Save each dataset as JSONL
DATA_DIR.mkdir(parents=True, exist_ok=True)

for name, records in [
    ("train.jsonl", train_data),
    ("validation.jsonl", val_data),
    ("test.jsonl", test_data),
]:
    with open(DATA_DIR / name, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + chr(10))

print("Total clean examples:", len(clean_data))
print("Training examples:", len(train_data))
print("Validation examples:", len(val_data))
print("Test examples:", len(test_data))
print("First training example:", train_data[0]["instruction"])
print("Files saved in:", DATA_DIR)

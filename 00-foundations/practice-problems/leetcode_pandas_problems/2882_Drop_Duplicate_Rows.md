# LeetCode 2882: Drop Duplicate Rows

## Problem Description

You are given a Pandas DataFrame named `customers` with three columns:

- `customer_id` (int)  
- `name` (string)  
- `email` (string)

Some rows contain duplicate email addresses. Your task is to **remove rows with duplicate emails** and **keep only the first occurrence** of each unique email address. :contentReference[oaicite:0]{index=0}

---

## Example

**Input DataFrame:**

| customer_id | name    | email               |
|-------------|---------|---------------------|
| 1           | Ella    | emily@example.com   |
| 2           | David   | michael@example.com |
| 3           | Zachary | sarah@example.com   |
| 4           | Alice   | john@example.com    |
| 5           | Finn    | john@example.com    |
| 6           | Violet  | alice@example.com   |

**Expected Output:**

| customer_id | name    | email               |
|-------------|---------|---------------------|
| 1           | Ella    | emily@example.com   |
| 2           | David   | michael@example.com |
| 3           | Zachary | sarah@example.com   |
| 4           | Alice   | john@example.com    |
| 6           | Violet  | alice@example.com   |

Explanation:  
For rows with the same `email`, only the first instance is kept (e.g., Alice is kept and Finn is removed because both have `john@example.com`). :contentReference[oaicite:1]{index=1}

---

## Solution

```python
import pandas as pd

def dropDuplicateEmails(customers: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows based on the 'email' column,
    keeping only the first occurrence.
    """
    return customers.drop_duplicates(subset=['email'])
```

---

## Explanation

- Pandas provides the method `.drop_duplicates()` to remove duplicate rows.  
- The `subset=['email']` argument tells Pandas to check only the `email` column for duplicates.  
- By default, `drop_duplicates()` keeps the first occurrence of each unique value.  
- The resulting DataFrame has only unique email addresses and preserves the original relative order of rows. :contentReference[oaicite:2]{index=2}

---

## Key Takeaways

- Use `df.drop_duplicates(subset=[...])` to drop rows with duplicate values in specific columns.  
- The default behavior of `drop_duplicates()` keeps the **first occurrence** and drops later ones.  
- This is a common data cleaning operation in Pandas.


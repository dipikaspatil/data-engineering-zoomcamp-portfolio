# LeetCode 2883: Drop Missing Data

## Problem Description

You are given a Pandas DataFrame `students` with the following columns:

- `student_id` (int)
- `name` (string)
- `age` (int)

Some rows contain **missing values** (null/NaN) in the `name` column.  
Your task is to **remove all rows where `name` is missing** and return the cleaned DataFrame. :contentReference[oaicite:0]{index=0}

---

## Example

**Input:**

| student_id | name    | age |
|------------|---------|-----|
| 32         | Piper   | 5   |
| 217        | None    | 19  |
| 779        | Georgia | 20  |
| 849        | Willow  | 14  |

**Output:**

| student_id | name    | age |
|------------|---------|-----|
| 32         | Piper   | 5   |
| 779        | Georgia | 20  |
| 849        | Willow  | 14  |

Explanation: Rows where `name` is missing have been removed. :contentReference[oaicite:1]{index=1}

---

## Solution

```python
import pandas as pd

def dropMissingData(students: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows where the 'name' column contains missing values.
    """
    return students.dropna(subset=["name"])
```

---

## Explanation

- Pandas’ `.dropna()` method removes rows with missing values.  
- Using `subset=["name"]` ensures that only rows with missing `name` values are dropped, leaving other columns intact.  
- By default, the first occurrence of each non‑missing value is kept and missing rows are removed. :contentReference[oaicite:2]{index=2}

---

## Key Takeaways

- Use `df.dropna(subset=[...])` to drop rows with missing values in specific columns.  
- This is a common data‑cleaning pattern when working with real‑world datasets.  
- `.notnull()` or `df[df["name"].notna()]` can also be used. :contentReference[oaicite:3]{index=3}


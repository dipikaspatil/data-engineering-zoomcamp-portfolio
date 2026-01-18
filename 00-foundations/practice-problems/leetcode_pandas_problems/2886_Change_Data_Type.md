# LeetCode 2886: Change Data Type

## Problem Description

You are given a Pandas DataFrame named `students` with the following columns:

- `student_id` (int)
- `name` (string)
- `age` (int)
- `grade` (float)

Some of the grades are stored as floating point numbers (e.g., `73.0`, `87.0`), but they represent whole numbers.  
Your task is to **convert the `grade` column from floats to integers** and return the updated DataFrame. :contentReference[oaicite:0]{index=0}

---

## Example

**Input DataFrame:**

| student_id | name  | age | grade |
|------------|-------|-----|-------|
| 1          | Ava   | 6   | 73.0  |
| 2          | Kate  | 15  | 87.0  |

**Expected Output DataFrame:**

| student_id | name  | age | grade |
|------------|-------|-----|-------|
| 1          | Ava   | 6   | 73    |
| 2          | Kate  | 15  | 87    |

---

## Solution

```python
import pandas as pd

def changeDatatype(students: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the 'grade' column from float to integer.
    """
    students["grade"] = students["grade"].astype(int)
    return students
```

---

## Explanation

- We use the Pandas `astype()` method to **change the data type** of the `grade` column from float to integer. :contentReference[oaicite:1]{index=1}  
- Since the original `grade` values are float representations of whole numbers (e.g., `73.0` → `73`), converting to `int` simply removes the decimal part. :contentReference[oaicite:2]{index=2}  
- The updated DataFrame has the `grade` column stored as integers, while all other columns remain unchanged.

---

## Notes

- If the `grade` column had **missing (`NaN`) values**, `astype(int)` would raise an error because integers cannot represent `NaN`. In that case, you could fill or handle missing values first (e.g., `fillna(0)` or similar) before converting.  
- Alternative conversion approaches include using a dictionary with `.astype({"grade": int})` to cast only specific columns.



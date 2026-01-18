# LeetCode Problem: Select Data

## Problem Description

You are given a Pandas DataFrame named `students` with the following columns:

- `student_id` (int)
- `name` (object)
- `age` (int)

Write a function to **select the `name` and `age`** of the student having `student_id = 101`.

---

## Example

**Input DataFrame:**

| student_id | name     | age |
|------------|----------|-----|
| 101        | Ulysses  | 13  |
| 53         | William  | 10  |
| 128        | Henry    | 6   |
| 3          | Henry    | 11  |

**Expected Output DataFrame:**

| name    | age |
|---------|-----|
| Ulysses | 13  |

---

## Solution

```python
import pandas as pd

def selectData(students: pd.DataFrame) -> pd.DataFrame:
    """
    Return only the 'name' and 'age' columns for the student
    whose student_id equals 101.
    """
    return students.loc[students['student_id'] == 101, ['name', 'age']]
```

---

## Explanation

- We use **boolean indexing** to filter the DataFrame to only rows where `student_id == 101`.  
- Then we select the specific columns we want — `name` and `age`.  
- `.loc[...]` lets us specify a **row condition** and a **list of column names** in one concise expression. :contentReference[oaicite:0]{index=0}

---

## Notes

- Using `[['name', 'age']]` (double brackets) ensures the result is a **DataFrame**, not a Series.  
- If no student has `student_id == 101`, the function will return an **empty DataFrame** with columns `name` and `age`.  

---

## Suggested filename

`select_data.md`

---

## Suggested Git commit message

```
Add LeetCode Pandas problem: Select Data
```

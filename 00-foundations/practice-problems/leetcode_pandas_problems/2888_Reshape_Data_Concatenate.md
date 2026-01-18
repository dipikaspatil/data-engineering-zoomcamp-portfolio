# LeetCode 2888: Reshape Data: Concatenate

## Problem Description

You are given two Pandas DataFrames `df1` and `df2`.  
Both DataFrames have the **same columns**:

- `student_id` (int)
- `name` (string/object)
- `age` (int)

Your task is to **concatenate the two DataFrames vertically** —  
that is, append all rows from `df2` *below* all rows from `df1` and return the combined DataFrame. :contentReference[oaicite:0]{index=0}

---

## Example

### Input

**DataFrame `df1`:**

| student_id | name   | age |
|------------|--------|-----|
| 1          | Mason  | 8   |
| 2          | Ava    | 6   |
| 3          | Taylor | 15  |
| 4          | Georgia| 17  |

**DataFrame `df2`:**

| student_id | name | age |
|------------|------|-----|
| 5          | Leo  | 7   |
| 6          | Alex | 7   |

### Expected Output

| student_id | name    | age |
|------------|---------|-----|
| 1          | Mason   | 8   |
| 2          | Ava     | 6   |
| 3          | Taylor  | 15  |
| 4          | Georgia | 17  |
| 5          | Leo     | 7   |
| 6          | Alex    | 7   |

---

## Solution

```python
import pandas as pd

def concatenateTables(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Vertically concatenate df1 and df2
    into a single DataFrame.
    """
    # Combine the DataFrames row-wise
    result = pd.concat([df1, df2], ignore_index=True)
    return result
```

---

## Explanation

- **`pd.concat()`** is the Pandas function used to combine DataFrames.  
- Passing a list `[df1, df2]` tells Pandas to stack `df2` below `df1`.  
- By default, `pd.concat()` concatenates along `axis=0` (rows).  
- `ignore_index=True` resets the resulting index to `0, 1, 2, …`.  
- This ensures a clean index without duplicate labels from the original DataFrames. :contentReference[oaicite:1]{index=1}

---

## Notes

- This operation **does not remove duplicates** — it simply stacks the tables.  
- If column names differ, Pandas will align them and fill missing spots with `NaN`.  
- For horizontal concatenation (adding columns), use `pd.concat(..., axis=1)` instead.

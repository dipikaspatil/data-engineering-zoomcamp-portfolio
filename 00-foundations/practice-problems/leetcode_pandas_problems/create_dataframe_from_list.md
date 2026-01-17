# LeetCode Problem: Create a DataFrame from List

## Problem Description

You are given a list of lists, `student_data`, where each inner list contains:
- `student_id` (int)
- `age` (int)

Your task is to **create a Pandas DataFrame** from this list, with the columns:
- "student_id"
- "age"

The **order of rows** should be the same as in `student_data`.

---

## Example

**Input:**

```python
student_data = [
    [1, 15],
    [2, 11],
    [3, 11],
    [4, 20]
]
```

**Expected Output DataFrame:**

| student_id | age |
|-----------:|----:|
| 1         | 15  |
| 2         | 11  |
| 3         | 11  |
| 4         | 20  |

---

## Solution

```python
import pandas as pd
from typing import List

def createDataframe(student_data: List[List[int]]) -> pd.DataFrame:
    """
    Create a DataFrame from a list of lists.
    
    Args:
        student_data: List of [student_id, age] entries
    
    Returns:
        pd.DataFrame with columns ["student_id", "age"]
    """
    return pd.DataFrame(student_data, columns=["student_id", "age"])
```

---

## Explanation

- `pd.DataFrame(data, columns=…)` treats each inner list as a **row**.  
- The `columns` argument assigns meaningful column names.  
- The order of rows is preserved, exactly as in the input list.

**Important Note:**
- Do **not** attempt to split `student_data[0]` and `student_data[1]` into columns — this will produce incorrect results because each inner list is a row, not a column.  
- This approach works for **any list of lists** of consistent length.

---



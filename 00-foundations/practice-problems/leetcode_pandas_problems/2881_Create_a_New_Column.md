# LeetCode 2881: Create a New Column

## Problem

You are given a Pandas DataFrame named `employees` with the following columns:

- `name` (string)
- `salary` (int)

Create a new column called **`bonus`** where:

```
bonus = salary * 2
```

Return the updated DataFrame.

---

## Example

### Input

| name  | salary |
|-------|--------|
| Piper | 4548   |
| Grace | 28150  |
| Georgia | 1103 |

### Output

| name  | salary | bonus |
|-------|--------|-------|
| Piper | 4548   | 9096  |
| Grace | 28150  | 56300 |
| Georgia | 1103 | 2206  |

---

## Solution

```python
import pandas as pd

def createBonusColumn(employees: pd.DataFrame) -> pd.DataFrame:
    employees["bonus"] = employees["salary"] * 2
    return employees
```

---

## Explanation

- Pandas allows **vectorized arithmetic operations** on columns.
- `employees["salary"] * 2` multiplies every salary value by `2`.
- Assigning it to a new column name (`"bonus"`) creates the column.
- No loops are required.

---

## Key Takeaways

- New columns can be created via direct assignment
- Vectorized operations are efficient and readable
- Pandas automatically aligns values row-wise

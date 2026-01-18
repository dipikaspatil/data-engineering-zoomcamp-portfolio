# LeetCode 2884: Modify Columns

## Problem Description

You are given a Pandas DataFrame named `employees` with the following columns:

- `name` (object)
- `salary` (int)

A company intends to give its employees a pay rise.  
Write a solution to **modify the `salary` column by multiplying each salary by 2**. :contentReference[oaicite:1]{index=1}

---

## Example

**Input DataFrame:**

| name     | salary |
|----------|--------|
| Jack     | 19666  |
| Piper    | 74754  |
| Mia      | 62509  |
| Ulysses  | 54866  |

**Output DataFrame:**

| name     | salary |
|----------|--------|
| Jack     | 39332  |
| Piper    | 149508 |
| Mia      | 125018 |
| Ulysses  | 109732 |

*Explanation:* Every salary has been doubled. :contentReference[oaicite:2]{index=2}

---

## Solution

```python
import pandas as pd

def modifySalaryColumn(employees: pd.DataFrame) -> pd.DataFrame:
    """
    Modify the existing salary column by doubling its values.
    """
    employees["salary"] = employees["salary"] * 2
    return employees
```

---

## Explanation

- We access the `salary` column using `employees["salary"]`.  
- Multiplying the entire column by `2` performs a **vectorized operation** on all rows at once.  
- The result replaces the original `salary` values with the doubled values.  
- Finally, we return the modified DataFrame. :contentReference[oaicite:3]{index=3}

---

## Key Takeaways

- **Vectorized operations** in Pandas allow you to efficiently modify entire columns without loops.  
- Use `df[column] = df[column] * factor` to **update values in place**.



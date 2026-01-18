# LeetCode 2891: Method Chaining

## Problem Description

You are given a Pandas DataFrame named `animals` with the following columns:

- `name` (object)
- `species` (object)
- `age` (int)
- `weight` (int)

Write a function to **list the names of animals that weigh strictly more than 100 kilograms**, **sorted by weight in descending order**.  
Complete the task in one line of code using **method chaining**. :contentReference[oaicite:1]{index=1}

---

## Example

**Input DataFrame:**

| name     | species | age | weight |
|----------|---------|-----|--------|
| Tatiana  | Snake   | 98  | 464    |
| Khaled   | Giraffe | 50  | 41     |
| Alex     | Leopard | 6   | 328    |
| Jonathan | Monkey  | 45  | 463    |
| Stefan   | Bear    | 100 | 50     |
| Tommy    | Panda   | 26  | 349    |

**Expected Output:**

| name     |
|----------|
| Tatiana  |
| Jonathan |
| Tommy    |
| Alex     |

Explanation: Only animals with `weight > 100` are included, then sorted by `weight` descending and only their `name`s are returned. :contentReference[oaicite:2]{index=2}

---

## Solution

```python
import pandas as pd

def findHeavyAnimals(animals: pd.DataFrame) -> pd.DataFrame:
    return (
        animals[animals["weight"] > 100]
        .sort_values(by="weight", ascending=False)[["name"]]
    )
```

---

## Explanation

- **Filter**: `animals["weight"] > 100` uses boolean indexing to keep only rows where `weight` is greater than 100.  
- **Sort**: `.sort_values(by="weight", ascending=False)` sorts these filtered rows by the `weight` column in descending order.  
- **Select**: `[['name']]` selects only the `name` column from the sorted results, returning a DataFrame of names.  
- These steps are **chained together in one expression** without intermediate variables — classic method chaining. :contentReference[oaicite:3]{index=3}

---

## Notes

- Using double brackets `[['name']]` ensures the result is a **DataFrame** (as required) rather than a Series.  
- This pattern — filter → sort → select — is a common Pandas data‑manipulation pipeline built via method chaining.  
- Method chaining keeps your code concise, readable, and expressive.



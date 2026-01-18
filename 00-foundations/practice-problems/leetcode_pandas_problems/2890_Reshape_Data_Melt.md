# LeetCode 2890: Reshape Data: Melt

## Problem Description

You are given a Pandas DataFrame named `report` with these columns:

- `product` (string)
- `quarter_1` (integer)
- `quarter_2` (integer)
- `quarter_3` (integer)
- `quarter_4` (integer)

Your task is to **reshape the DataFrame from a wide format into a long format** such that:

- Each row represents a **product’s sales in one quarter**
- There is a `quarter` column holding the quarter name
- There is a `sales` column holding the corresponding sales value  
- The `product` column is repeated for each quarter row

This transformation is also known as “melting” the data. :contentReference[oaicite:0]{index=0}

---

## Example

**Input DataFrame:**

| product     | quarter_1 | quarter_2 | quarter_3 | quarter_4 |
|-------------|-----------|-----------|-----------|-----------|
| Umbrella    | 417       | 224       | 379       | 611       |
| SleepingBag | 800       | 936       | 93        | 875       |

**Expected Output DataFrame:**

| product     | quarter    | sales |
|-------------|------------|-------|
| Umbrella    | quarter_1  | 417   |
| SleepingBag | quarter_1  | 800   |
| Umbrella    | quarter_2  | 224   |
| SleepingBag | quarter_2  | 936   |
| Umbrella    | quarter_3  | 379   |
| SleepingBag | quarter_3  | 93    |
| Umbrella    | quarter_4  | 611   |
| SleepingBag | quarter_4  | 875   |

---

## Solution

```python
import pandas as pd

def meltTable(report: pd.DataFrame) -> pd.DataFrame:
    """
    Reshape the DataFrame from wide to long format.
    """
    return pd.melt(
        report,
        id_vars=["product"],
        var_name="quarter",
        value_name="sales"
    )
```

---

## Explanation

- Use `pd.melt()` to **unpivot** the wide format DataFrame to long format.  
- `id_vars=["product"]` keeps the `product` column as the identifier.  
- `var_name="quarter"` names the new column containing the old column names.  
- `value_name="sales"` names the new column with the corresponding values.  
- Each row in the result corresponds to a product’s sales in one quarter. :contentReference[oaicite:1]{index=1}

---

## Notes

- `pd.melt()` is the Pandas method designed for reshaping wide tables into long (tidy) tables.  
- If the DataFrame had other columns you wanted to keep, include them in `id_vars`.  
- The order of rows in the result reflects the stacking of each “melted” column.


# LeetCode 2887: Fill Missing Data

## Problem Description

You are given a Pandas DataFrame named `products` with the following columns:

- `name` (string)
- `quantity` (int)
- `price` (int)

Some rows in the `quantity` column contain missing (null) values.  
Your task is to **replace all missing values in the `quantity` column with `0`** and return the updated DataFrame.:contentReference[oaicite:1]{index=1}

---

## Example

**Input DataFrame:**

| name            | quantity | price |
|-----------------|----------|-------|
| Wristwatch      | None     | 135   |
| WirelessEarbuds | None     | 821   |
| GolfClubs       | 779      | 9319  |
| Printer         | 849      | 3051  |

**Expected Output DataFrame:**

| name            | quantity | price |
|-----------------|----------|-------|
| Wristwatch      | 0        | 135   |
| WirelessEarbuds | 0        | 821   |
| GolfClubs       | 779      | 9319  |
| Printer         | 849      | 3051  |

---

## Solution

```python
import pandas as pd

def fillMissingValues(products: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in the 'quantity' column with 0.
    """
    products["quantity"] = products["quantity"].fillna(0)
    return products
```

---

## Explanation

- The Pandas `.fillna()` method replaces missing values (`NaN` or `None`) with the specified value.  
- Here, `products["quantity"].fillna(0)` returns a Series where all nulls in the `quantity` column are replaced with `0`.  
- Assigning it back to `products["quantity"]` updates the DataFrame.  
- The result has no missing values in the `quantity` column, and all original non‑missing values are preserved.:contentReference[oaicite:2]{index=2}

---

## Notes

- You can also fill missing values **in place** with:

  ```python
  products["quantity"].fillna(0, inplace=True)
  ```

- If you needed to ensure an integer type (sometimes float results from columns with `NaN`), use:

  ```python
  products["quantity"] = products["quantity"].fillna(0).astype(int)
  ```

- This pattern of handling missing data is common in real‑world data cleaning workflows.

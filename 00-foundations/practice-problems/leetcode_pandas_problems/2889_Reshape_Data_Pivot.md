# LeetCode 2889: Reshape Data: Pivot

## Problem Description

You are given a Pandas DataFrame named `weather` with the following columns:

- `city` (object)
- `month` (object)
- `temperature` (int)

Your task is to **pivot** this data so that:

- Each **row** represents a specific month  
- Each **city** becomes its own column  
- The **temperature** values fill the cells at the intersections

Return the pivoted DataFrame. :contentReference[oaicite:0]{index=0}

---

## Example

**Input DataFrame:**

| city         | month    | temperature |
|--------------|----------|-------------|
| Jacksonville | January  | 13          |
| Jacksonville | February | 23          |
| ElPaso       | January  | 20          |
| ElPaso       | February | 6           |

**Expected Output:**

| month    | ElPaso | Jacksonville |
|----------|--------|--------------|
| January  | 20     | 13           |
| February | 6      | 23           |

---

## Solution

```python
import pandas as pd

def pivotTable(weather: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot the weather DataFrame to have months as rows, cities as columns,
    and temperature values in the cells.
    """
    return weather.pivot(index="month", columns="city", values="temperature")
```

---

## Explanation

- We use the Pandas `.pivot()` method to reshape the DataFrame.  
- `index="month"` makes the unique months the **row labels**.  
- `columns="city"` makes each unique city a **column**.  
- `values="temperature"` fills the cells with corresponding temperature values.  
- The pivot operation reorganizes the long‑format table into wide format, making it easier to compare cities’ temperatures by month. :contentReference[oaicite:1]{index=1}

---

## Notes

- If there are **duplicate (month, city)** combinations, `.pivot()` will raise a `ValueError`. In those cases, you can use `.pivot_table()` with an aggregation function.  
- If some city/month combinations are missing, the resulting DataFrame will contain `NaN` for those cells.

---


---


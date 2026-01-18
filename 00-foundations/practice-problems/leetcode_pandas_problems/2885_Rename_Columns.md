# LeetCode 2885: Rename Columns

## Problem Description

You are given a Pandas DataFrame called `students` with the following columns:

- `id` (int)  
- `first` (string)  
- `last` (string)  
- `age` (int)

Rename the columns as follows:

- `id` → `student_id`  
- `first` → `first_name`  
- `last` → `last_name`  
- `age` → `age_in_years`  

Return the updated DataFrame with the new column names. :contentReference[oaicite:0]{index=0}

---

## Example

**Input DataFrame:**

| id | first   | last     | age |
|----|---------|----------|-----|
| 1  | Mason   | King     | 6   |
| 2  | Ava     | Wright   | 7   |
| 3  | Taylor  | Hall     | 16  |
| 4  | Georgia | Thompson | 18  |
| 5  | Thomas  | Moore    | 10  |

**Expected Output DataFrame:**

| student_id | first_name | last_name | age_in_years |
|------------|------------|-----------|--------------|
| 1          | Mason      | King      | 6            |
| 2          | Ava        | Wright    | 7            |
| 3          | Taylor     | Hall      | 16           |
| 4          | Georgia    | Thompson  | 18           |
| 5          | Thomas     | Moore     | 10           |

---

## Solution

```python
import pandas as pd

def renameColumns(students: pd.DataFrame) -> pd.DataFrame:
    students = students.rename(
        columns={
            "id": "student_id",
            "first": "first_name",
            "last": "last_name",
            "age": "age_in_years",
        }
    )
    return students
```

---

## Explanation

- Pandas’ `.rename()` method allows you to rename specific columns by supplying a dictionary mapping old names → new names.  
- The `columns=` parameter tells pandas which labels to update.  
- The method returns a new DataFrame (unless `inplace=True` is used), so we assign it back to `students` before returning. :contentReference[oaicite:1]{index=1}

---

## Notes / Tips

- You can also use `inplace=True` with `.rename()` to modify the DataFrame without reassigning:

  ```python
  students.rename(
      columns={
          "id": "student_id",
          "first": "first_name",
          "last": "last_name",
          "age": "age_in_years",
      },
      inplace=True
  )
  ```

- Make sure the column names in the `columns` dict match exactly (case‑sensitive) the current column names. :contentReference[oaicite:2]{index=2}


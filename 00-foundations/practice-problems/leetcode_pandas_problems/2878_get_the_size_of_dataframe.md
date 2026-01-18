# LeetCode Problem: Get the Size of a DataFrame

## Problem Description

You are given a Pandas DataFrame named `players`.

Your task is to return the **size of the DataFrame** as a list containing:
- number of rows
- number of columns

The result must be returned as a **list of two integers**:

```
[number_of_rows, number_of_columns]
```

---

## Example

If the input DataFrame `players` looks like this:

| player_id | name  | age |
|----------:|-------|----:|
| 1         | Alice | 25  |
| 2         | Bob   | 30  |
| 3         | Carol | 22  |

Then the output should be:

```python
[3, 3]
```

---

## Solution

```python
import pandas as pd
from typing import List

def getDataframeSize(players: pd.DataFrame) -> List[int]:
    """
    Return the size of the DataFrame as:
    [number of rows, number of columns]
    """
    return list(players.shape)
```

---

## Explanation

- Every Pandas DataFrame has a `.shape` attribute.
- `.shape` returns a tuple in the form:

```python
(rows, columns)
```

- Converting it to a list using `list()` matches the expected output format.

### Example

```python
players.shape
# (3, 3)

list(players.shape)
# [3, 3]
```

---

## Key Takeaways

- Use `.shape` to quickly get DataFrame dimensions
- Convert the tuple to a list when required by the problem


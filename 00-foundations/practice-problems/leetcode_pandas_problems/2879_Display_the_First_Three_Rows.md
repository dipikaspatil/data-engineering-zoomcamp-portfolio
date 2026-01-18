# Why use `head(3)` instead of `iloc[0:3)` in Pandas?

## Context

In the LeetCode problem **“Display the First Three Rows”**, the goal is to return the first three rows of a DataFrame.

Two common approaches are:

```python
employees.head(3)
```

and

```python
employees.iloc[0:3]
```

Both produce the same result, but `head(3)` is generally preferred.

---

## Recommended Approach

```python
employees.head(3)
```

### Reasons

- Clearly expresses intent: **“get the first 3 rows”**
- More readable and beginner-friendly
- Idiomatic Pandas style
- Safely handles DataFrames with fewer than 3 rows

---

## Alternative Approach (Also Correct)

```python
employees.iloc[0:3]
```

### When to use `iloc`

- When you need **positional indexing**
- When selecting **both rows and columns** by position

Example:

```python
employees.iloc[0:3, [0, 2]]
```

---

## Comparison

| Feature | `head(3)` | `iloc[0:3]` |
|------|----------|------------|
| Returns first 3 rows | ✅ | ✅ |
| Readability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Beginner friendly | ✅ | ⚠️ |
| Idiomatic Pandas | ✅ | ⚠️ |
| Supports column slicing | ❌ | ✅ |

---

## Why LeetCode Prefers `head()`

- LeetCode Pandas problems emphasize **clarity over flexibility**
- `head()` communicates intent without needing indexing knowledge
- Easier to review and understand in interviews

---

## Key Takeaway

> Use `head()` when your goal is **simply to get the first N rows**  
> Use `iloc` when you need **precise positional control**

Both are valid, but **`head()` is the cleaner and more expressive choice** for this problem.

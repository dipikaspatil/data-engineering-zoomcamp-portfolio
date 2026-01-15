### source - https://www.kaggle.com/learn/pandas
## 1 - Creating, Reading and Writing

### Getting started
To use pandas, you'll typically start with the following line of code.

```python
import pandas as pd
```

### Creating data
There are two core objects in pandas:

1 - DataFrame

2 - Series

#### 1 - DataFrame
* A DataFrame is a table. It contains an array of individual entries, each of which has a certain value. 

* Each entry corresponds to a row (or record) and a column.

* We are using the pd.DataFrame() constructor to generate these DataFrame objects. The syntax for declaring a new one is a dictionary whose keys are the column names (Bob and Sue in below example), and whose values are a list of entries. This is the standard way of constructing a new DataFrame, and the one you are most likely to encounter.

For example, consider the following simple DataFrame:

```python
pd.DataFrame({'Yes': [50, 21], 'No': [131, 2]})

'''
Output - 
	Yes	No
0	50	131
1	21	2
'''
```

* DataFrame entries are not limited to integers. For instance, here's a DataFrame whose values are strings:

```python
pd.DataFrame({'Bob': ['I liked it.', 'It was awful.'], 'Sue': ['Pretty good.', 'Bland.']})

'''
Output - 

	Bob	            Sue
0	I liked it.	    Pretty good.
1	It was awful.	Bland.
'''

```

* The dictionary-list constructor assigns values to the column labels, but just uses an ascending count from 0 (0, 1, 2, 3, ...) for the row labels. Sometimes this is OK, but oftentimes we will want to assign these labels ourselves.

* The list of row labels used in a DataFrame is known as an Index. We can assign values to it by using an index parameter in our constructor:

```python
pd.DataFrame({'Bob': ['I liked it.', 'It was awful.'], 
              'Sue': ['Pretty good.', 'Bland.']},
             index=['Product A', 'Product B'])

'''
Output - 
	        Bob	            Sue
Product A	I liked it.	    Pretty good.
Product B	It was awful.	Bland.
'''
```

#### 2 - Series

* A Series, by contrast, is a sequence of data values. If a DataFrame is a table, a Series is a list. And in fact you can create one with nothing more than a list:

```python
pd.Series([1, 2, 3, 4, 5])

'''
Output - 
0    1
1    2
2    3
3    4
4    5
dtype: int64
'''
```


* A Series is, in essence, a single column of a DataFrame. So you can assign row labels to the Series the same way as before, using an index parameter. However, a Series does not have a column name, it only has one overall name:

```python
pd.Series([30, 35, 40], index=['2015 Sales', '2016 Sales', '2017 Sales'], name='Product A')

'''
Output-  
2015 Sales    30
2016 Sales    35
2017 Sales    40
Name: Product A, dtype: int64
'''
```

* The Series and the DataFrame are intimately related. It's helpful to think of a DataFrame as actually being just a bunch of Series "glued together".

### Reading data files

* We'll use the pd.read_csv() function to read the data into a DataFrame.

```python
wine_reviews = pd.read_csv("../input/wine-reviews/winemag-data-130k-v2.csv")
```

* We can use the shape attribute to check how large the resulting DataFrame is:

```python
wine_reviews.shape

'''
Output - 
(129971, 14)

130,000 records split across 14 different columns

'''
```

* We can examine the contents of the resultant DataFrame using the head() command, which grabs the first five rows:

```python
wine_reviews.head()
```
| Unnamed: 0 | Country  | Description                                       |
| ---------- | -------- | ------------------------------------------------- |
| 0          | Italy    | Aromas include tropical fruit, broom, brimston... |
| 1          | Portugal | This is ripe and fruity, a wine that is smooth... |
| 2          | US       | Tart and snappy, the flavors of lime flesh and... |
| 3          | US       | Pineapple rind, lemon pith and orange blossom ... |
| 4          | US       | Much like the regular bottling from 2012, this... |


* The pd.read_csv() function is well-endowed, with over 30 optional parameters you can specify. For example, you can see in this dataset that the CSV file has a built-in index, which pandas did not pick up on automatically. To make pandas use that column for the index (instead of creating a new one from scratch), we can specify an index_col.

```python
wine_reviews = pd.read_csv("../input/wine-reviews/winemag-data-130k-v2.csv", index_col=0)
wine_reviews.head()
```
| Country  | Description                                       | Designation                        |
| -------- | ------------------------------------------------- | ---------------------------------- |
| Italy    | Aromas include tropical fruit, broom, brimston... | Vulkà Bianco                       |
| Portugal | This is ripe and fruity, a wine that is smooth... | Avidagos                           |
| US       | Tart and snappy, the flavors of lime flesh and... | NaN                                |
| US       | Pineapple rind, lemon pith and orange blossom ... | Reserve Late Harvest               |
| US       | Much like the regular bottling from 2012, this... | Vintner's Reserve Wild Child Block |

### Writing data files

* DataFrame to a CSV file is very straightforward using df.to_csv()

```python
import pandas as pd

# Sample DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 22],
    'City': ['New York', 'Los Angeles', 'Chicago']
}

df = pd.DataFrame(data)

# Write to CSV
df.to_csv('output.csv', index=False)  # index=False avoids writing row numbers


'''
Output - 
This will create a file called output.csv in the current working directory.
'''
```

* Advanced Options

```python
# Include index
df.to_csv('output_with_index.csv', index=True)

# Specify separator (e.g., tab-separated)
df.to_csv('output.tsv', sep='\t', index=False)

# Handle missing values
df.to_csv('output_na.csv', index=False, na_rep='N/A')

# Write only specific columns
df.to_csv('output_columns.csv', columns=['Name', 'City'], index=False)
```

## 2 - Indexing, Selecting & Assigning

* Consider dataframe - reviews

* In Python, we can access the property of an object by accessing it as an attribute. A book object, for example, might have a title property, which we can access by calling book.title. Columns in a pandas DataFrame work in much the same way.

* Hence to access the country property of reviews we can use:

```python
reviews.country
'''
Output -

0           Italy
1           Portugal
            ...   
129969      France
129970      France
Name: country, Length: 129971, dtype: object
'''
```

* If we have a Python dictionary, we can access its values using the indexing ([]) operator. We can do the same with columns in a DataFrame:

```python
reviews['country']
'''
Output -

0           Italy
1           Portugal
            ...   
129969      France
129970      France
Name: country, Length: 129971, dtype: object
'''
```

* Note - 

* 1 - reviews.country and reviews['country'] are almost same when column name is clean. But it won't work when there are spaces in column name.

* 2 - indexing operator [] does have the advantage that it can handle column names with reserved characters in them (e.g. if we had a country providence column, reviews.country providence wouldn't work).

```python
# Dot notation fails for 'reviews count'
print(reviews.reviews count)  # ❌ SyntaxError
print(reviews['reviews count'])  # ✅ Works
```

* ✅ Rule of Thumb

 1 - Safe for any column: use reviews['column_name']

 2 - Shortcut for simple, clean column names: reviews.column_name


* Doesn't a pandas Series look kind of like a fancy dictionary? It pretty much is, so it's no surprise that, to drill down to a single specific value, we need only use the indexing operator [] once more:

```python
reviews['country'][0] # Output - 'Italy'
```

#### Indexing in pandas

* Apart from indexing operator from python, Pandas has its own accessor operators, loc and iloc

* index-based selection - iloc

```python
# To select the first row of data in a DataFrame
reviews.iloc[0]

# To get all column with iloc
reviews.iloc[:, 0]

# To select the country column from just the first, second, and third row
reviews.iloc[:3, 0]

# To select just the second and third entries
reviews.iloc[1:3, 0]

# It's also possible to pass a list
reviews.iloc[[0, 1, 2], 0] # return 0,1,2 records

# Negative numbers can be used in selection. last five elements of the dataset
reviews.iloc[-5:]
```

* Label-based selection - loc

```python
# to get the first country in reviews
reviews.loc[0, 'country']

# To get all entries of specific columns
reviews.loc[:, ['taster_name', 'taster_twitter_handle', 'points']]
```

* Difference between iloc and loc - 

```
df.iloc[0:1000] will return 1000 entries. End index exclusive.
df.loc[0:1000] return 1001 of them. End index inclusive.

To get 1000 elements using loc, you will need to go one lower and ask for df.loc[0:999].
```

#### Manipulating the index

* The set_index() method can be used to do the job. Here is what happens when we set_index to the title field:

```python
reviews.set_index("title")
```

![Dataframe set index](../images/dataframe_set_index.png)



import ast
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer


def ast_eval(s, alt_fcn=None):
    """Load lists from CSV; wrapper around ast.literal_eval() to catch exceptions"""
    
    try:
        result = ast.literal_eval(s)
    except:
        if alt_fcn:
            try:
                result = alt_fcn()
            except:
                result = s
        else:
            result = s

    return result


def columns_where_rows_differ(df):
    """Get a list of the columns for which the row values differ"""
    
    return df.nunique(axis=0).where(lambda x: x>1, axis=0).dropna().index.tolist()


def get_unique_col_values(df, col):
    """Get alphabetized list of unique values in a column of single- or multi-select options"""

    # Convert all values in column to lists
    df[col] = df[col].apply(lambda s: ast_eval(s, alt_fcn=lambda s: [x.strip() for x in str(s).split(',')]))
    df[col] = df[col].apply(lambda d: d if isinstance(d, list) else [])

    # One-hot encode column of lists
    mlb = MultiLabelBinarizer(sparse_output=True)
    df_onehot = pd.DataFrame.sparse.from_spmatrix(
        mlb.fit_transform(df[col]),
        index=df.index,
        columns=mlb.classes_)

    # Get count for each unique item
    df_sum = pd.DataFrame(df_onehot.sum()).sort_values(0, axis=0, ascending=False).transpose()

    # Print alphabetized list of unique values
    for i, row in df_sum.iterrows():
        for item in sorted(list(row.index), key=lambda s: (s.lower(), s)):
            print(item)

    return sorted(list(row.index))


def print_groupby(gb):
    """Print pandas groupby object"""
    
    for key, item in gb:
        print(key)
        print(gb.get_group(key), "\n")

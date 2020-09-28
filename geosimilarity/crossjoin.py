import pandas as pd

def df_crossjoin(df1, df2, **kwargs):
    """
    From: https://gist.github.com/internaut/5a653317688b14fd0fc67214c1352831
    Make a cross join (cartesian product) between two dataframes by using a
    constant temporary key. Also sets a MultiIndex which is the cartesian
    product of the indices of the input dataframes.
    See: https://github.com/pydata/pandas/issues/5401

    Parameters
    ----------
    df1 : DataFrame
    df2 : DataFrame
    kwargs : keyword arguments that will be passed to pd.merge()

    Returns
    -------
    res : DataFrame
        Cartesian join of df1 and df2
    """

    # Create temporary key to merge the DataFrames on
    df1['_tmpkey'] = 1
    df2['_tmpkey'] = 1

    # Merge DataFrames and create MultiIndex
    res = pd.merge(df1, df2, on='_tmpkey', **kwargs).drop('_tmpkey', axis=1)
    res.index = pd.MultiIndex.from_product((df1.index, df2.index))

    # Drop temporary key
    df1.drop('_tmpkey', axis=1, inplace=True)
    df2.drop('_tmpkey', axis=1, inplace=True)

    return res

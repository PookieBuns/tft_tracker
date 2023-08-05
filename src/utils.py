import pandas as pd
from sqlalchemy import CursorResult
def convert_to_df(result: CursorResult):
    columns = result.columns()
    data = result.fetchall()
    return pd.DataFrame(data, columns=columns)

import pandas as pd


def push_data_to_db(data_file):
    data = pd.read_csv(data_file)
    # authors =
    # authors.to_sql(
    #     name="authors", con=db_con.get_db_engine(), if_exists="append", index=False
    # )
    print(data)
    return data

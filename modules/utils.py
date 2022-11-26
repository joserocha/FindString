"""
    utils.py
"""
from typing import Optional
from rich.table import Table
from rich import box
import pandas as pd


pd.set_option("display.max_rows", None)


def dataframe_to_table(data_frame: pd.DataFrame,
                       rich_table: Table,
                       show_index: bool = False,
                       index_name: Optional[str] = None) -> Table:
    """ dataframe_to_table """
    if show_index:
        index_name = str(index_name) if index_name else ""
        rich_table.add_column(index_name)

    for column in data_frame.columns:
        rich_table.add_column(str(column))

    for index, value_list in enumerate(data_frame.values.tolist()):
        row = [str(index)] if show_index else []
        row += [str(x) for x in value_list]
        rich_table.add_row(*row)

    return rich_table


def create_dataframe(data, output):
    df = pd.DataFrame(data, columns=["Namespace", "Kubernete's Object", "Resource Scanned", "Details"])

    if output == "simple":
        distinct_df = df[["Namespace", "Kubernete's Object", "Resource Scanned"]]
        return distinct_df.drop_duplicates()
    else:
        return df


def create_table():
    t = Table(show_header=True, header_style="bold yellow", show_lines=True)
    t.row_styles = ["none", "light_cyan1"]
    t.box = box.ASCII
    return t
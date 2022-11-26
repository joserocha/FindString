"""
    main.py
"""
import argparse
from modules.client import Client
from modules.utils import *
from rich.console import Console
from rich.panel import Panel
from rich.padding import Padding
from joblib import Parallel, delayed
import time


start = time.time()

# add command line arguments
args = argparse.ArgumentParser()

args.add_argument("--find",
                  "-f",
                  help="string to be find it",
                  type=str)
args.add_argument("--output",
                  "-o",
                  choices=["simple", "detailed"],
                  help="specify the type of output",
                  type=str)
args.add_argument("--verbose",
                  "-v",
                  help="increase output verbosity",
                  action="store_true")

params = args.parse_args()

if __name__ == "__main__":
    find_string = getattr(params, "find").lower()
    output_format = getattr(params, "output").lower()
    is_verbose = getattr(params, "verbose")

    client_obj = Client()
    cluster_name = client_obj.get_cluster_name()

    # print the header
    console_obj = Console()
    console_obj.print(Panel.fit("[yellow bold].: SEARCH FOR STRING IN KUBERNETES CLUSTER"))
    console_obj.print(Padding(f"----"
                              f"\nLooking for: {find_string}"
                              f"\nCluster name: {cluster_name}"
                              f"\nOutput format {output_format}"
                              f"\n----", (0, 0, 1, 0)))

    # get all namespaces
    namespaces = client_obj.get_all_namespaces()

    # progression / threads
    with console_obj.status("[bold green]Working on namespaces...") as status:
        Parallel(n_jobs=6, prefer="threads")(
            delayed(client_obj.search_string)(namespace, find_string, is_verbose) for namespace in namespaces.items)

    if output_format == "simple":
        df_to_pod = create_dataframe(client_obj.pods, "simple")
        df_to_secret = create_dataframe(client_obj.secrets, "simple")
    else:
        df_to_pod = create_dataframe(client_obj.pods, "detailed")
        df_to_secret = create_dataframe(client_obj.secrets, "detailed")

    console_obj.print(dataframe_to_table(df_to_pod, create_table()))
    console_obj.print(dataframe_to_table(df_to_secret, create_table()))

    console_obj.print(Padding("----", (1, 0, 0, 0)))
    console_obj.print(Panel.fit("[yellow bold].:: THE END ::."))

    end = time.time()

    total_time = end - start
    print("\n" + str(total_time))

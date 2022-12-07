"""
    main.py
"""
import argparse
import itertools
from multiprocessing import Pool
from functools import partial
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.padding import Padding
from modules.server import Cluster
import modules.client as client
import modules.utils as utils


# create the parser
args = argparse.ArgumentParser()

# add the arguments
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

# execute the parse_args() method
params = args.parse_args()


if __name__ == "__main__":
    # retrieve arguments
    find_string = getattr(params, "find").lower()
    output_format = getattr(params, "output").lower()
    is_verb = getattr(params, "verbose")

    # init
    cluster_name = Cluster.get_cluster_name()
    console_obj = Console()

    # header
    console_obj.print(Panel.fit("[yellow bold].: SEARCH FOR STRING IN KUBERNETES CLUSTER"))
    console_obj.print(Padding(f"----"
                              f"\nLooking for: {find_string}"
                              f"\nCluster name: {cluster_name}"
                              f"\nOutput format {output_format}"
                              f"\n----", (0, 0, 1, 0)))

    # get all namespaces
    namespaces = client.get_all_namespaces()

    # status of the current task
    with console_obj.status("[bold green]Working on pods...") as p_status:

        # trick to make status text readable when verbose True
        sleep(0.5) if is_verb else sleep(0)

        # search in the pods for the desired term, in parallel mode
        with Pool(16) as p:
            p_result = p.map(partial(client.search_pod, is_verb, find_string), namespaces.items)

    # status of the current task
    with console_obj.status("[bold green]Working on secrets...") as s_status:

        # trick to make status text readable when verbose True
        sleep(0.5) if is_verb else sleep(0)

        # search in the secrets for the desired term, in parallel mode
        with Pool(16) as p:
            s_result = p.map(partial(client.search_secret, is_verb, find_string), namespaces.items)

    # removing empty elements and flatten the nested list
    p_result_filtered = list(itertools.chain(*(filter(None, p_result))))
    s_result_filtered = list(itertools.chain(*(filter(None, s_result))))

    # convert panda's dataframe to rich's table format
    if output_format == "simple":
        df_to_pod = utils.create_dataframe(p_result_filtered, "simple")
        df_to_secret = utils.create_dataframe(s_result_filtered, "simple")
    else:
        df_to_pod = utils.create_dataframe(p_result_filtered, "detailed")
        df_to_secret = utils.create_dataframe(s_result_filtered, "detailed")

    # print the result
    console_obj.print(utils.dataframe_to_table(df_to_pod, utils.create_table()))
    console_obj.print(utils.dataframe_to_table(df_to_secret, utils.create_table()))

    # footer
    console_obj.print(Padding("----", (1, 0, 0, 0)))
    console_obj.print(Panel.fit("[yellow bold].:: THE END ::."))

"""
    _client.py
"""
from base64 import b64decode as b64
from modules.server import Cluster


cluster_obj = Cluster()


def get_all_namespaces():
    """ get_all_namespaces """
    return cluster_obj.get_all_namespaces()


def search_pod(verbose, string, n):
    """ search_pod """

    # create an empty list
    p_list = []

    # verbose
    if verbose:
        print(f"[{n.metadata.name}] - pod - started!")

    # retrieve all pods from a namespace
    p_namespace = cluster_obj.get_pods_by_namespace(n.metadata.name)

    # return if namespace hasn't pods
    if p_namespace is None:
        if verbose:
            print(f"[{n.metadata.name}] - pod - failed retrieving pods.")
            print(f"[{n.metadata.name}] - done!")
        return -1

    # iterate through pods
    for p in p_namespace.items:

        # if pod isn't running try another one
        if p.status.phase != "Running":
            if verbose:
                print(f"[{n.metadata.name}] - pod - pod not ok. Trying another one.")
            continue

        # execute env command
        # if response is None, try another pod
        response = cluster_obj.exec_command_pod(p.metadata.name, n.metadata.name)
        if response is None:
            if verbose:
                print(f"[{n.metadata.name}] - pod - failed scanning pod.")
            continue

        # iterate through elements trying
        # to match the desired string
        break_out_flag = False
        for i, item in enumerate(response.split("\n")):
            if item.find(string) > -1:
                p_list.append([n.metadata.name.lower(),
                               "Pod",
                               f"name: {p.metadata.name.lower()}",
                               f"{item}"])

            # after read all elements
            # we can exit the main loop
            if (i + 1) == len(response.split("\n")):
                if verbose:
                    print(f"[{n.metadata.name}] - pod - success scanning pod.")
                    print(f"[{n.metadata.name}] - done!")
                break_out_flag = True
                break
        if break_out_flag:
            break

    return p_list


def search_secret(verbose, string, n):
    """ search_secret """

    # create an empty list
    s_list = []

    if verbose:
        print(f"[{n.metadata.name}] - secrets - started!")

    # retrieve all secrets from a namespace
    s_namespace = cluster_obj.get_secrets_by_namespace(n.metadata.name)

    # return if namespace hasn't secrets
    if s_namespace is None:
        if verbose:
            print(f"[{n.metadata.name}] - secrets - failed retrieving secrets.")
        return -1

    for s in s_namespace.items:
        if s.type == "Opaque" and s.data is not None:
            for key, value in s.data.items():
                k = key.lower() if key != "" else "emp_k"

                try:
                    v = b64(value).decode("utf-8").lower() if value != "" else "emp_v"

                    if k.find(string) > -1 or v.find(string) > -1:
                        s_list.append([n.metadata.name.lower(),
                                       "Secret",
                                       f"type: {s.type.lower()}, "
                                       f"name: {s.metadata.name.lower()}",
                                       f"{k}={v}"])
                except UnicodeDecodeError:
                    if verbose:
                        print(f"[{n.metadata.name}] - secrets - failed decoding value of key {k}.")
                    continue

    if verbose:
        print(f"[{n.metadata.name}] - secrets - success reading secrets.")
        print(f"[{n.metadata.name}] - done!")

    return s_list

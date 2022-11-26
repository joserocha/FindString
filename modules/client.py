"""
    client.py
"""
from base64 import b64decode as b64
from modules.server import Cluster
from multiprocessing import Manager


class Client:
    """ Client """

    @property
    def pods(self):
        return self._pods

    @pods.setter
    def pods(self, value):
        self._pods = value

    @property
    def secrets(self):
        return self._secrets

    @secrets.setter
    def secrets(self, values):
        self._secrets = values

    def __init__(self):
        """ init """
        manager = Manager()
        self.cluster_obj = Cluster()
        self.pods = manager.list()
        self.secrets = manager.list()

    def get_cluster_name(self):
        """ get_cluster_name """
        return self.cluster_obj.get_cluster_config()

    def get_all_namespaces(self):
        """ get_all_namespaces """
        return self.cluster_obj.get_all_namespaces()

    def search_string_in_pod(self, namespace, search_text, verbose):
        """ search_string_in_pod """

        # create an empty list
        pod_data = []

        # verbose
        if verbose:
            print(f"[{namespace.metadata.name}] - pod - started!")

        # retrieve all pods per namespace
        pods_namespace = self.cluster_obj.get_pods_by_namespace(namespace.metadata.name)

        # check for pods iterate through it try to execute
        # "env" command and search for a specific string
        if pods_namespace is None:
            if verbose:
                print(f"\t[{namespace.metadata.name}] - pod - failed retrieving pods.")
        else:
            for pod in pods_namespace.items:
                if pod.status.phase == "Running":
                    response = self.cluster_obj.exec_command_pod(pod.metadata.name, namespace.metadata.name)

                    if response is None:
                        if verbose:
                            print(f"\t[{namespace.metadata.name}] - pod - failed scanning pod.")
                        continue

                    lines = response.split("\n")
                    for line in lines:
                        if line.find(search_text) > -1:
                            pod_data.append([namespace.metadata.name.lower(),
                                             "Pod",
                                             f"name: {pod.metadata.name.lower()}",
                                             f"{line}"])
                break

            # verbose
            if verbose:
                print(f"\t[{namespace.metadata.name}] - pod - success scanning pod.")

            return pod_data

    def search_string_in_secret(self, namespace, search_text, verbose):
        """ search_string_in_secret """

        # create an empty list
        secret_data = []

        if verbose:
            print(f"[{namespace.metadata.name}] - secrets - started!")

        # retrieve all secrets per namespace
        secrets_namespace = self.cluster_obj.get_secrets_by_namespace(namespace.metadata.name)

        # check for secrets iterate through it get keys
        # and values and search for a specific string
        if secrets_namespace is None:
            if verbose:
                print(f"\t[{namespace.metadata.name}] - secrets - failed retrieving secrets.")
        else:
            for secret in secrets_namespace.items:
                if secret.type == "Opaque" and secret.data is not None:
                    for key, value in secret.data.items():
                        try:
                            k = key.lower() if key != "" else "emp_k"
                            v = b64(value).decode("utf-8").lower() if value != "" else "emp_v"

                            if k.find(search_text) > -1 or v.find(search_text) > -1:
                                secret_data.append([namespace.metadata.name.lower(),
                                                    "Secret",
                                                    f"type: {secret.type.lower()}, "
                                                    f"name: {secret.metadata.name.lower()}",
                                                    f"{k}={v}"])
                        except UnicodeDecodeError:
                            continue
            if verbose:
                print(f"\t[{namespace.metadata.name}] - secrets - success reading secrets.")

        if verbose:
            print(f"[{namespace.metadata.name}] - done!")

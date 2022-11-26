"""
    server.py
"""
from kubernetes.client import ApiException
from kubernetes.stream import stream
from kubernetes import config, client


class Cluster:
    """ Cluster """

    def __init__(self):
        """ init """
        config.load_kube_config("~/.kube/config")
        self.api = client.CoreV1Api()

    @staticmethod
    def get_cluster_config():
        """ get_cluster_name """
        ctx = config.list_kube_config_contexts()[1]
        return ctx["context"]["cluster"].split("_")[::-1][0]

    def get_all_namespaces(self):
        """ get_all_namespaces """
        return self.api.list_namespace()

    def get_pods_by_namespace(self, namespace):
        """ get_pods_by_namespace """
        try:
            return self.api.list_namespaced_pod(namespace=namespace)
        except ApiException:
            return None

    def get_secrets_by_namespace(self, namespace):
        """ get_secrets_by_namespace """
        try:
            return self.api.list_namespaced_secret(namespace=namespace)
        except ApiException:
            return None

    def exec_command_pod(self, pod, namespace):
        """ exec_command_pod """
        try:
            return stream(self.api.connect_get_namespaced_pod_exec,
                          pod,
                          namespace,
                          command="env",
                          stderr=True,
                          stdin=False,
                          stdout=True,
                          tty=False).lower()
        except ApiException:
            return None

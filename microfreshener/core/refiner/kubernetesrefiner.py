from .irefiner import Refiner
from ..model import MicroToscaModel
from ..model.nodes import KIngress, KService, KProxy

from ..model.groups import Edge
from ..logging import MyLogger

from nested_lookup import nested_lookup

import yaml

logger = MyLogger().get_logger()


class KubernetesRefiner(Refiner):

    def __init__(self, yml_file):
        self.yml_file = yml_file
        self.kdeployments = []
        self.kservices = []
        self.kingresses = []

    def Refine(self, microtosca: MicroToscaModel)->MicroToscaModel:
        self.load_kubernetes_objects()
        self.microtosca = microtosca
        for kservice in self.kservices:
            self.refine_kservice(kservice)
        for kingress in self.kingresses:
            self.refine_kingress(kingress)
        return self.microtosca

    def load_kubernetes_objects(self):
        with open(self.yml_file, 'r') as stream:
            docs = yaml.load_all(stream)
            for doc in docs:
                self._load_kobject(doc)

    def get_kdeployment_with_label(self, selector):
        kd_matching = []
        for kdeployemnt in self.kdeployments:
            for label in kdeployemnt.labels:
                if selector.get(label[0]) == label[1]:
                    kd_matching.append(kdeployemnt)
        return kd_matching

    def refine_kingress(self, kingress):
        self.microtosca.add_node(kingress)
        for backend in kingress.backends:
            node = self.microtosca[backend]
            edge = self.microtosca.get_edge_of_node(node)
            if edge != None:
                edge.remove_node(node)
            kingress.add_interaction(node, with_timeout=False, with_circuit_breaker=False, with_dynamic_discovery=True)
        if len(list(self.microtosca.edges)) == 0:
            edge = Edge("k-edge")
        else:
            edge = list(self.microtosca.edges)[0]
        edge.add_member(kingress)
        self.microtosca.add_group(edge)

    def refine_kservice(self, kservice):
        kd_matching = self.get_kdeployment_with_label(kservice.selector)
        for kdeployment in kd_matching:
            selected_node = self.microtosca[kdeployment.name]
            incoming_interactions = list(selected_node.incoming_interactions)
            for incoming in incoming_interactions:
                if isinstance(incoming.source, KService):
                    raise Exception(
                        f"{selected_node} has already a kservice defined")
            for incoming in incoming_interactions:
                incoming.source.remove_interaction(incoming)
                incoming.source.add_interaction(kservice, False, False, True)
            kservice.add_interaction(selected_node)
            self.microtosca.add_node(kservice)

    def _load_kobject(self, kobject):
        # if(kobject.get("kind") == "Deployment"):
        #     kdeploy = self._load_kdeployment(kobject)
        #     self.kdeployments.append(kdeploy)
        # if(kobject.get("kind") == "Service"):
        #     kservice = self._load_kservice(kobject)
        #     self.kservices.append(kservice)
        if kobject.get("kind") == "Ingress":
            ingress = self._load_kingress(kobject)
            self.kingresses.append(ingress)

    def _load_kdeployment(self, kobject):
        kdeployment = None
        if "metadata" in kobject.keys():
            metadata = kobject.get("metadata")
            if "name" in metadata.keys():
                name = metadata.get("name")
                kdeployment = KDeployment(name)
            else:
                raise Exception("name of kdepoyment not found")
            if "labels" in metadata.keys():
                labels = metadata.get("labels")
                for label in labels.items():
                    kdeployment.add_label(label)
        return kdeployment

    def _load_kservice(self, kobject):
        kservice = None
        if "metadata" in kobject.keys():
            metadata = kobject.get("metadata")
            if "name" in metadata.keys():
                name = f"k{metadata.get('name')}"
            else:
                raise Exception(
                    f"Name is missing in service {kobject}")
        if "spec" in kobject.keys():
            spec = kobject.get("spec")
            if "selector" in spec.keys():
                selector = spec.get("selector")
                #  <key: value>
                #  the service target all the pods with a label that match the key:value
        return KService(name, selector)

    def _load_kingress(self, kobject):
        name = None
        if "metadata" in kobject.keys():
            metadata = kobject.get("metadata")
            if "name" in metadata.keys():
                name = metadata.get("name")
            else:
                raise Exception(f"Name is missing in {kobject}")
        if "spec" in kobject.keys():
            spec = kobject.get("spec")
            serviceNames = nested_lookup('serviceName', spec)
            kingress = KIngress(name, serviceNames)
        return kingress

    def retrieve_nested_value(mapping, key_of_interest):
        mappings = [mapping]
        while mappings:
            mapping = mappings.pop()
            try:
                items = mapping.items()
            except AttributeError:
                # we didn't store a mapping earlier on so just skip that value
                continue

            for key, value in items:
                if key == key_of_interest:
                    yield value
                else:
                    # type of the value will be checked in the next loop
                    mappings.append(value)


class KDeployment():
    def __init__(self, name):
        self._name = name
        self._labels = []  # [{<key>:<value>}]

    @property
    def name(self):
        return self._name

    @property
    def labels(self):
        return self._labels

    def add_label(self, label):
        self._labels.append(label)

    def __str__(self):
        return '{} ({})'.format(self.name, 'KDeployement')

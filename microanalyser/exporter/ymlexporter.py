import sys
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

from ..model import MicroToscaModel
from ..model  import RunTimeInteraction, DeploymentTimeInteraction
from ..model import Root, Service, Database, CommunicationPattern, MessageBroker, MessageRouter
from ..model.groups import RootGroup, Edge, Team
from ..model.type import MICROTOSCA_RELATIONSHIPS_INTERACT_WITH, MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY
from ..model.type import MICROTOSCA_NODES_SERVICE, MICROTOSCA_NODES_DATABASE, MICROTOSCA_NODES_MESSAGE_BROKER, MICROTOSCA_NODES_MESSAGE_ROUTER
from ..model.type import  MICROTOSCA_GROUPS_EDGE, MICROTOSCA_GROUPS_TEAM
from ..importer.ymltype import YML_RUN_TIME, YML_DEPLOYMENT_TIME
from .iexporter import Exporter
from ..errors import ExporterError

class MyYAML(YAML):
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


class YMLExporter(Exporter):

    def __init__(self):
        self.yaml = MyYAML()

    # Export a microModel Oject to YML format
    # @params:  microModel
    # @return:  string
    def Export(self, micro_model: MicroToscaModel):
        return self.yaml.dump(self._to_dict(micro_model))

    def _to_dict(self, micro_model):

        yml_dict = self._get_metadata()

        topology_template = {}
        node_templates = {}
        for node in micro_model.nodes:
            node_templates[node.name] = self._transform_node_template(node)
        topology_template['node_templates'] = node_templates


        groups = {}
        for group in micro_model.groups:
            groups[group.name] = self._transform_group(group)
        topology_template["groups"] = groups

        topology_template['relationship_templates'] = self.build_timedout_relationship_template()

        yml_dict['topology_template'] = topology_template
        return yml_dict

    def build_timedout_relationship_template(self):
        return {"timedout": {"type": MICROTOSCA_RELATIONSHIPS_INTERACT_WITH, "properties": {MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY: True}}}

    def _get_metadata(self):
        d_metadata = dict(tosca_definitions_version="tosca_simple_yaml_1_0", description="",
                          imports=[{"micro": "../../data/micro-tosca-types.yml"}])
        return d_metadata

    def _transform_group(self, group: RootGroup):
        d_group = {}
        group_type = ""
        if (isinstance(group, Edge)):
            group_type = MICROTOSCA_GROUPS_EDGE
        elif (isinstance(group, Team)):
            group_type = MICROTOSCA_GROUPS_TEAM
        else:
            raise ExporterError("{} group not recognized".format(group))
        d_group['type'] = group_type

        members = [member.name for member in group.members]
        d_group['members'] = members
        return d_group

    def _transform_node_template(self, node: Root):
        # {"order":{"type":"micro.nodes.Service", "requirements":[{YML_RUN_TIME: "order_db"}]}}
        node_templates = dict()
        d_node = {}
        node_type = ""
        if(isinstance(node, Service)):
            node_type = MICROTOSCA_NODES_SERVICE
        elif(isinstance(node, Database)):
            node_type = MICROTOSCA_NODES_DATABASE
        elif(isinstance(node, MessageBroker)):
            node_type = MICROTOSCA_NODES_MESSAGE_BROKER
        elif(isinstance(node, MessageRouter)):
            node_type = MICROTOSCA_NODES_MESSAGE_ROUTER
        else:
            raise ExporterError(f"Node {node} not recognized")
        d_node['type'] = node_type

        requirements = []
        for rel in node.relationships:
            requirements.append(self._transform_relationship(rel))
        if(requirements):
            d_node['requirements'] = requirements
        return d_node

    def _transform_relationship(self, rel):
        d_rel = {}
        if(isinstance(rel, DeploymentTimeInteraction)):
            d_rel[YML_DEPLOYMENT_TIME] = rel.target.name
        elif(isinstance(rel, RunTimeInteraction)):
            if(rel.timeout and not rel.circuit_breaker and not rel.dynamic_discovery):
                d_rel[YML_RUN_TIME] = {"node": rel.target.name, "relationship": "t"}
            elif(not rel.timeout and rel.circuit_breaker and not rel.dynamic_discovery):
                d_rel[YML_RUN_TIME] = {"node": rel.target.name, "relationship": "c"}
            elif(not rel.timeout and  not rel.circuit_breaker and rel.dynamic_discovery):
                d_rel[YML_RUN_TIME] = {"node": rel.target.name, "relationship": "d"}
            elif(rel.timeout and rel.circuit_breaker and not rel.dynamic_discovery):
                d_rel[YML_RUN_TIME] = {"node": rel.target.name, "relationship": "tc"}
            elif(rel.timeout and not rel.circuit_breaker and rel.dynamic_discovery):
                d_rel[YML_RUN_TIME] = {"node": rel.target.name, "relationship": "td"}
            elif(not rel.timeout and rel.circuit_breaker and rel.dynamic_discovery):
                d_rel[YML_RUN_TIME] = {"node": rel.target.name, "relationship": "cd"}
            elif(rel.timeout and rel.circuit_breaker and rel.dynamic_discovery):
                d_rel[YML_RUN_TIME] = {"node": rel.target.name, "relationship": "tcd"}
            else:
                d_rel[YML_RUN_TIME] = rel.target.name
        else:
            raise ExporterError('{} relationship not recognized.'.format(rel))
        return d_rel

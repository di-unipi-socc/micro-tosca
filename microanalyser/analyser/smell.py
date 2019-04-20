from typing import List


class NodeSmell(object):

    def __init__(self, node, interactions=[]):
        self._node = node
        self._interactions = interactions  # TODO: rename in moulds (muffe )???

    @property
    def node(self):
        return self._node

    @property
    def caused_by(self):
        return self._interactions

    def to_dict(self):
        return {"name": self.name, "node": self.node.name, "cause": [interation.to_dict() for interation in self._interactions]}

    def add_bad_interactions(self, interactions):
        self._interactions = interactions

    def add_single_interaction(self, interaction):
        self._interactions.append(interaction)

    def isEmpty(self):
        return len(self._interactions) == 0


class GroupSmell(object):

    def __init__(self, group, affected_nodes):
        self._group = group
        self._affected_nodes = affected_nodes

    @property
    def group(self):
        return self._group

    @property
    def caused_by(self):
        return self._affected_nodes

    def to_dict(self):
        return {"name": self.name, "group": self._group.name, "cause": [node.name for node in self._affected_nodes]}

    def isEmpty(self):
        return len(self._affected_nodes) == 0


class NoApiGatewaySmell(GroupSmell):
    name: str = "NoApiGateway"

    def __init__(self, node, interactions):
        super(NoApiGatewaySmell, self).__init__(node, interactions)

    def __str__(self):
        return 'NoApiGateway({})'.format(super(NodeSmell, self).__str__())

    def to_dict(self):
        sup_dict = super(NoApiGatewaySmell, self).to_dict()
        return {**sup_dict, **{"refactorings": [{"name": "Add Api Gateway", "description": "Add an Api Gateway between the external user"}]}}


class EndpointBasedServiceInteractionSmell(NodeSmell):
    name: str = "EndpointBasedServiceInteractionSmell"

    def __init__(self, node, interactions=[]):
        super(EndpointBasedServiceInteractionSmell,
              self).__init__(node, interactions)

    def __str__(self):
        return 'EndpointBasedServiceInteractionSmell({})'.format(super(NodeSmell, self).__str__())

    def to_dict(self):
        sup_dict = super(EndpointBasedServiceInteractionSmell, self).to_dict()
        return {**sup_dict, **{"refactorings": [
            {"name": "Add Service Discovery",
                "description": "Add Service discovery"},
            {"name": "Add Message Router", "description": "Add a message router"},
            {"name": "Add Message Broker", "description": " Add message broker"}
        ]}}


class WobblyServiceInteractionSmell(NodeSmell):
    name: str = "WobblyServiceInteractionSmell"

    def __init__(self, node, interactions=[]):
        super(WobblyServiceInteractionSmell, self).__init__(node, interactions)

    def __str__(self):
        return 'WobblyServiceInteractionSmell({})'.format(super(NodeSmell, self).__str__())

    def to_dict(self):
        sup_dict = super(WobblyServiceInteractionSmell, self).to_dict()
        return {**sup_dict, **{"refactorings": [
            {"name": "Add Message Broker", "description": "Add Message broker"},
            {"name": "Add Circuit Breaker", "description": " Add Circuit breaker"},
            {"name": "Use Timeouts", "description": "Use timeouts"}]}}


class SharedPersistencySmell(NodeSmell):
    name: str = "SharedPersistencySmell"

    def __init__(self, node, interactions=[]):
        super(SharedPersistencySmell, self).__init__(node, interactions)

    def __str__(self):
        return 'SharedPersistencySmell({})'.format(super(NodeSmell, self).__str__())

    def to_dict(self):
        sup_dict = super(SharedPersistencySmell, self).to_dict()
        return {**sup_dict, **{"refactorings": [
            {"name": "Merge services",
                "description": "Merge services accesing the same database"},
            {"name": "Split Database", "description": "Split the database."},
            {"name": "Add Data Manager", "description": " Add Data manager"}]}}

from unittest import TestCase

from microanalyser.importer import JSONImporter, YMLImporter
from microanalyser.exporter import JSONExporter



class TestJSONTranformer(TestCase):

    @classmethod
    def setUpClass(self):
        file = 'data/examples/helloworld.yml'
        self.importer = YMLImporter()
        self.microtosca = self.importer.Import(file)
        self.tranformer = JSONExporter()

    def test_dictionary_groups(self):
        edgeGroup = self.microtosca.get_group('edgenodes')
        group_dict = self.tranformer._transform_group(edgeGroup)
        self.assertEqual("name" in group_dict, True)
        self.assertEqual("type" in group_dict, True)
        self.assertEqual("members" in group_dict, True)

    def test_squad_group(self): 
        squad =  self.microtosca.get_group("team1")
        squad_dict = self.tranformer._transform_group(squad)
        self.assertEqual(squad_dict['name'], "team1")
        self.assertEqual("type" in squad_dict, True)
        self.assertEqual(squad_dict['type'], "squadgroup")

        squad2 =  self.microtosca.get_group("team2")
        squad_dict = self.tranformer._transform_group(squad2)
        self.assertEqual('name' in squad_dict, True)
        self.assertEqual(squad_dict['name'], "team2")
        self.assertEqual("type" in squad_dict, True)
        self.assertEqual(squad_dict['type'], "squadgroup")
      





import unittest
import time
from unittest.mock import Mock

from retrain import retrain_wksp

class Retrain_Wksp_Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_workspace = {'name': 'Test', 'language': 'en', 
                            'description': 'Mock', 'workspace_id': '1234'}
        self.lots_of_workspaces = [self.mock_workspace] * 30
        self.little_workspaces = [self.mock_workspace] * 5
        self.single_workspace = [self.mock_workspace]
        self.intents = [{'intent': 'Testing', 'description': 'Testing Desc'}] * 10
        self.intent_is_none = None
    
    def reset_mocks(self, *args):
        for mock in args:
            mock.reset_mock()
        
        retrain_wksp.Variables.global_wksp_counter = 0

    
    def test_lots_of_workspaces(self):
        retrain_wksp.get_workspaces = Mock(return_value=self.lots_of_workspaces)
        retrain_wksp.update_intent_desc = Mock()
        retrain_wksp.update_intent_desc.return_value.get_status_code.return_value = 200
        retrain_wksp.get_intents = Mock(return_value=self.intents[0])
        time.sleep = Mock(return_value=None)

        retrain_wksp.retrain_wksp()

        retrain_wksp.get_workspaces.assert_called_once()
        self.assertEqual(retrain_wksp.get_intents.call_count, 30)
        self.assertEqual(retrain_wksp.update_intent_desc.call_count, 30)
        time.sleep.assert_called_once()
        self.assertEqual(retrain_wksp.Variables.global_wksp_counter, 0)
        
        self.reset_mocks(retrain_wksp.get_workspaces, retrain_wksp.update_intent_desc, 
                        retrain_wksp.get_intents, time.sleep)
    
    def test_small_workspace(self):
        retrain_wksp.get_workspaces = Mock(return_value=self.little_workspaces)
        retrain_wksp.update_intent_desc = Mock()
        retrain_wksp.update_intent_desc.return_value.get_status_code.return_value = 200
        retrain_wksp.get_intents = Mock(return_value=self.intents[0])
        time.sleep = Mock(return_value=None)

        retrain_wksp.retrain_wksp()

        retrain_wksp.get_workspaces.assert_called_once()
        self.assertEqual(retrain_wksp.get_intents.call_count, 5)
        self.assertEqual(retrain_wksp.update_intent_desc.call_count, 5)
        self.assertEqual(time.sleep.call_count, 0)
        self.assertEqual(retrain_wksp.Variables.global_wksp_counter, 5)

        self.reset_mocks(retrain_wksp.get_workspaces, retrain_wksp.update_intent_desc, 
                        retrain_wksp.get_intents, time.sleep)
    
    def test_errors(self):
        retrain_wksp.get_workspaces = Mock(return_value=self.single_workspace)
        retrain_wksp.get_intents = Mock(return_value=None)
        retrain_wksp.get_entities = Mock(return_value=None)
        retrain_wksp.save_workspace = Mock(return_value=None)
        
        retrain_wksp.retrain_wksp()

        retrain_wksp.save_workspace.assert_not_called()
        self.reset_mocks(retrain_wksp.save_workspace)

        retrain_wksp.get_intents = Mock(return_value=self.intents[0])
        retrain_wksp.update_intent_desc = Mock()
        retrain_wksp.update_intent_desc.return_value.get_status_code.return_value = 403
        retrain_wksp.retrain_wksp()
        
        retrain_wksp.save_workspace.assert_called_once()
        self.reset_mocks(retrain_wksp.get_workspaces, retrain_wksp.get_intents, retrain_wksp.save_workspace)

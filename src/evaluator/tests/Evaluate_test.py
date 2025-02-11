from tests.TestClient import TestClient
from modes.EvaluateMode import evaluateMode
import asyncio

class TestEvaluate:
    
    def test_simple_evaluate(self):
        test_client = TestClient()
        asyncio.run(evaluateMode({"expression": "1+1", "environment": {}}, test_client))
        assert not test_client.isError()
        
        response = test_client.getResponse()
        
        assert response['result'] == '2 = 2'
        
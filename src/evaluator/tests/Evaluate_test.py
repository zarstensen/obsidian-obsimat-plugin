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
        
    def test_matrix_evaluate(self):
        test_client = TestClient()
        asyncio.run(evaluateMode({"expression": "2 \\cdot \n\\begin{bmatrix} 1 \\\\\\ 1 \\end{bmatrix}", "environment": {}}, test_client))
        assert not test_client.isError()
        
        response = test_client.getResponse()
        
        assert response['result'] == r'2 \left[\begin{matrix}1\\1\end{matrix}\right] = \left[\begin{matrix}2\\2\end{matrix}\right]'
        
from django.test import TestCase, Client
from django.urls import reverse
import json

class ApiIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_api_root(self):
        """Verify the root API endpoint returns 200 and correct metadata."""
        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'online')
        self.assertIn('endpoints', data)

    def test_health_check(self):
        """Verify the health check endpoint."""
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'healthy')

    def test_visualizer_fallback(self):
        """Verify visualizer falls back to local simulation when AI fails/missing."""
        url = reverse('generate-steps')
        payload = {"user_code": "int x = 10; int y = 5;"}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['source'], 'fallback_local')
        self.assertIn('steps', data)

    def test_adversary_fallback(self):
        """Verify adversary falls back to heuristics when AI fails/missing."""
        url = reverse('adversary-attack')
        payload = {"user_code": "void foo() { int* p = new int; }"}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['source'], 'heuristic')
        self.assertIn('memory_leak', data['vulnerability_categories'])

    def test_sandbox_mock(self):
        """Verify sandbox uses mock success when g++ is missing."""
        url = reverse('code-execute')
        payload = {"user_code": "int main() { return 0; }"}
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data['status'], ['mock_success', 'success'])

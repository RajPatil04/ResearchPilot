"""Unit tests for ResearchPilot AI FastAPI backend endpoints."""

import io
import unittest
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.state import backend_state


class TestBackendAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("model", data)
        self.assertIn("has_api_key", data)

    def test_models_endpoint(self):
        resp = self.client.get("/api/models")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("models", data)
        self.assertTrue(len(data["models"]) >= 2)
        model_ids = [m["id"] for m in data["models"]]
        self.assertIn("gemma-4-26b-a4b-it", model_ids)

    def test_connect_validation_empty_key(self):
        resp = self.client.post("/api/connect", json={"api_key": ""})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("cannot be empty", resp.json()["detail"].lower())

    def test_load_sample_paper(self):
        resp = self.client.post("/api/documents/sample")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("id", data)
        self.assertEqual(data["filename"], "sample_paper_researchpilot.pdf")
        self.assertGreater(data["page_count"], 0)
        self.assertTrue(data["is_active"])

        # Check document listed
        doc_list_resp = self.client.get("/api/documents")
        self.assertEqual(doc_list_resp.status_code, 200)
        docs = doc_list_resp.json()
        self.assertTrue(any(d["id"] == data["id"] for d in docs))

        # Check citation search
        doc_id = data["id"]
        cit_resp = self.client.get(f"/api/documents/{doc_id}/citations?q=benchmark+accuracy")
        self.assertEqual(cit_resp.status_code, 200)
        citations = cit_resp.json()
        self.assertIsInstance(citations, list)
        self.assertTrue(len(citations) > 0)
        self.assertIn("SR-1", citations[0]["id"])

        # Check page image rendering
        img_resp = self.client.get(f"/api/documents/{doc_id}/pages/1/image")
        self.assertEqual(img_resp.status_code, 200)
        self.assertEqual(img_resp.headers["content-type"], "image/png")
        self.assertTrue(img_resp.content.startswith(b"\x89PNG\r\n\x1a\n"))

    def test_conversations_endpoints(self):
        resp = self.client.get("/api/conversations")
        self.assertEqual(resp.status_code, 200)
        convs = resp.json()
        self.assertIsInstance(convs, list)

        # Create new conversation
        create_resp = self.client.post("/api/conversations")
        self.assertEqual(create_resp.status_code, 200)
        new_conv = create_resp.json()
        self.assertIn("id", new_conv)

    def test_agent_investigate_endpoint(self):
        # Ensure sample paper is loaded
        sample_resp = self.client.post("/api/documents/sample")
        doc_id = sample_resp.json()["id"]

        agent_req = {
            "query": "Investigate dataset and benchmark numbers",
            "document_id": doc_id,
            "max_steps": 3
        }
        resp = self.client.post("/api/agent/investigate", json=agent_req)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("execution_trace", data)
        self.assertGreater(data["tool_calls_count"], 0)

    def test_export_endpoint(self):
        req = {
            "title": "Quantum Error Correction",
            "export_type": "summary",
            "content": "### Plain Overview\nFault-tolerant qubits."
        }
        resp = self.client.post("/api/export", json=req)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers["content-type"], "text/markdown; charset=utf-8")
        self.assertIn("Fault-tolerant qubits", resp.text)


if __name__ == "__main__":
    unittest.main()

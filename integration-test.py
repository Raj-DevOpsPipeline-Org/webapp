import unittest
from app import app


class IntegrationTest(unittest.TestCase):
    def test_healthz(self):
        print("Running test_healthz...")

        client = app.test_client()
        response = client.get("/healthz")
        print(f"Received status code: {response.status_code}")

        self.assertEqual(
            response.status_code,
            200,
            msg=f"Expected status code 200, got {response.status_code}",
        )

        if response.status_code == 200:
            print("Test ran successfully with status code 200!")
        else:
            print("Test did not run successfully.")


if __name__ == "__main__":
    unittest.main()

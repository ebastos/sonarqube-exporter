import os
import json
from unittest.mock import MagicMock

os.environ['SONAR_USER'] = "user"
os.environ['SONAR_PASSWORD'] = "password"
os.environ['INFLUX_USER'] = "influx_user"
os.environ['INFLUX_PASSWORD'] = "influx_password"
os.environ['INFLUX_DB'] = "influx_db"

from sonar_client import SonarApiClient, Project


def test_new_sonarapiclient():
    client = SonarApiClient("user", "password")
    assert client.user == "user"
    assert client.passwd == "password"

def test_get_all_ids():
    with open("test_data/mock_all_ids.json") as f:
        mock_data = json.loads(f.read())
    client = SonarApiClient("user", "password")
    client._make_request = MagicMock(return_value=mock_data)
    output = client.get_all_ids('/api/components/search?qualifiers=TRK')
    assert len(output) == 11
    assert "our-projects.authman" in output[0].values()

def test_get_all_available_metrics():
    with open("test_data/mock_all_metrics.json") as f:
        mock_data = json.loads(f.read())
    client = SonarApiClient("user", "password")
    client._make_request = MagicMock(return_value=mock_data)
    output = client.get_all_available_metrics('/api/components/search?qualifiers=TRK')
    assert len(output) == 100
    assert "new_technical_debt" in output

def test_get_measures_by_component_id():
    with open("test_data/mock_measures.json") as f:
        mock_data = json.loads(f.read())
    client = SonarApiClient("user", "password")
    client._make_request = MagicMock(return_value=mock_data)
    output = client.get_measures_by_component_id('/api/measures/component?component=asdf')
    assert len(output) == 69
    assert "reliability_remediation_effort" in output[0]['metric']
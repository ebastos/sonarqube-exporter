import os
import json
from pytest_mock import mocker
from unittest.mock import MagicMock
from influxdb import InfluxDBClient
from datetime import datetime
from freezegun import freeze_time
from test_data.outputs import PREPARED_OUTPUT

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


def test_project():
    project = Project(identifier="abc", key="abc")
    assert project.id == "abc"
    assert project.key == "abc"
    assert project.metrics is None

def test_set_metrics():
    project = Project(identifier="abc", key="abc")
    project.set_metrics("abc")
    assert project.metrics == "abc"

@freeze_time("2020-01-01")
def test_export_metrics(mocker):

    with open("test_data/mock_measures.json") as f:
        mock_data = json.loads(f.read())
    client = SonarApiClient("user", "password")
    client._make_request = MagicMock(return_value=mock_data)
    measures = client.get_measures_by_component_id('/api/measures/component?component=asdf')
    
    mock_influx = mocker.patch.object(InfluxDBClient, 'write_points')

    project = Project(identifier="abc", key="abc")
    project.set_metrics(measures)
    project.export_metrics()
    mock_influx.assert_called_with(PREPARED_OUTPUT)

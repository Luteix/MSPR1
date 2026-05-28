from unittest.mock import patch

from app import create_app


def test_get_recent_alertes_route_returns_alertes():
    app = create_app()
    client = app.test_client()

    mock_alertes = [
        {'idAlerte': 9, 'idMesure': 31},
        {'idAlerte': 8, 'idMesure': 30}
    ]

    with patch('controllers.dashboard_controller.DashboardService.get_recent_alertes', return_value=mock_alertes) as mock_get_recent_alertes:
        response = client.get('/api/alertes/recentes?limit=2')

    assert response.status_code == 200
    assert response.get_json() == mock_alertes
    mock_get_recent_alertes.assert_called_once_with(2)


def test_get_recent_alertes_route_supports_legacy_alias():
    app = create_app()
    client = app.test_client()

    mock_alertes = [{'idAlerte': 7, 'idMesure': 29}]

    with patch('controllers.dashboard_controller.DashboardService.get_recent_alertes', return_value=mock_alertes):
        response = client.get('/api/alertes/recent')

    assert response.status_code == 200
    assert response.get_json() == mock_alertes

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from sqlalchemy import func
from services.dashboard_service import DashboardService
from models import LotGrains, Entrepot, Pays, Mesure, Alerte, StatutLot, Exploitation

# =============================================================================
# TESTS POUR DashboardService
# =============================================================================

@patch('services.dashboard_service.get_db')
def test_get_dashboard_summary_success(mock_get_db):
    """
    SC├ëNARIO: On demande le r├®sum├® du dashboard.
    QUAND: get_dashboard_summary est appel├®e.
    ALORS: Elle doit retourner les m├®triques globales et le r├®sum├® par pays.
    """
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session

    # Cr├®ation des mocks persistants hors de la fonction side_effect
    lot_query_mock = MagicMock()
    lot_filter_mock = MagicMock()
    lot_filter_mock.count.side_effect = [10, 1] # stockés, périmés
    lot_filter_mock.filter.return_value = lot_filter_mock
    lot_query_mock.filter.return_value = lot_filter_mock
    
    lot_join_filter_mock = MagicMock()
    lot_join_filter_mock.count.side_effect = [5] # nb_lots for pays 1
    lot_join_filter_mock.filter.return_value = lot_join_filter_mock
    lot_join_filter_mock.distinct.return_value.count.side_effect = [2, 2]
    join_once = lot_query_mock.join.return_value
    join_twice = join_once.join.return_value
    join_three = join_twice.join.return_value
    join_twice.filter.return_value = lot_join_filter_mock
    join_three.filter.return_value = lot_join_filter_mock
    join_three.join.return_value.filter.return_value = lot_join_filter_mock

    entrepot_query_mock = MagicMock()
    entrepot_query_mock.count.return_value = 4
    entrepot_join_mock = MagicMock()
    entrepot_join_mock.filter.return_value.count.return_value = 3
    entrepot_query_mock.join.return_value = entrepot_join_mock

    pays_query_mock = MagicMock()
    mock_pays = MagicMock()
    mock_pays.idPays = 1
    mock_pays.nom = 'Testland'
    pays_query_mock.all.return_value = [mock_pays]

    exp_query_mock = MagicMock()
    exp_query_mock.filter.return_value.count.return_value = 2
    
    scalar_query_mock = MagicMock()
    scalar_mock = MagicMock()
    scalar_mock.scalar.return_value = datetime(2024, 5, 21)
    scalar_query_mock.join.return_value.join.return_value.filter.return_value = scalar_mock

    def mock_query_side_effect(model):
        if model is LotGrains:
            return lot_query_mock
        elif model is Entrepot:
            return entrepot_query_mock
        elif model is Pays:
            return pays_query_mock
        elif model is Exploitation:
            return exp_query_mock
        else:
            return scalar_query_mock

    mock_session.query.side_effect = mock_query_side_effect

    # --- ACT ---
    result = DashboardService.get_dashboard_summary()

    # --- ASSERT ---
    assert mock_get_db.called
    
    # V├®rifier les m├®triques globales
    assert result['metrics']['lotsStockes'] == 10
    assert result['metrics']['lotsAlerte'] == 2
    assert result['metrics']['lotsPerimes'] == 1
    assert result['metrics']['entrepotsActifs'] == 4

    # V├®rifier le r├®sum├® par pays
    assert len(result['summaryByCountry']) == 1
    country_summary = result['summaryByCountry'][0]
    assert country_summary['pays']['nom'] == 'Testland'
    assert country_summary['nbExploitations'] == 2
    assert country_summary['nbEntrepots'] == 3
    assert country_summary['nbLots'] == 5
    assert country_summary['lotsEnAlerte'] == 2
    assert country_summary['derniereMesure'] is not None

    mock_session.close.assert_called_once()


@patch('services.dashboard_service.get_db')
def test_get_dashboard_summary_filters_only_active_lots(mock_get_db):
    """
    SCÉNARIO: On demande le résumé du dashboard.
    QUAND: des lots ont déjà une date de sortie.
    ALORS: seuls les lots actifs (non sortis) doivent être comptés.
    """
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session

    lot_query_mock = MagicMock()
    lot_filter_mock = MagicMock()
    lot_filter_mock.count.side_effect = [7, 1]
    lot_filter_mock.filter.return_value = lot_filter_mock
    lot_query_mock.filter.return_value = lot_filter_mock

    lot_join_filter_mock = MagicMock()
    lot_join_filter_mock.count.side_effect = [4]
    lot_join_filter_mock.filter.return_value = lot_join_filter_mock
    lot_join_filter_mock.distinct.return_value.count.side_effect = [1, 1]
    join_once = lot_query_mock.join.return_value
    join_twice = join_once.join.return_value
    join_three = join_twice.join.return_value
    join_twice.filter.return_value = lot_join_filter_mock
    join_three.filter.return_value = lot_join_filter_mock
    join_three.join.return_value.filter.return_value = lot_join_filter_mock

    entrepot_query_mock = MagicMock()
    entrepot_query_mock.count.return_value = 0

    pays_query_mock = MagicMock()
    mock_pays = MagicMock()
    mock_pays.idPays = 1
    mock_pays.nom = 'Testland'
    pays_query_mock.all.return_value = [mock_pays]

    exp_query_mock = MagicMock()
    exp_query_mock.filter.return_value.count.return_value = 0

    scalar_query_mock = MagicMock()
    scalar_mock = MagicMock()
    scalar_mock.scalar.return_value = datetime(2024, 5, 21)
    scalar_query_mock.join.return_value.join.return_value.filter.return_value = scalar_mock

    def mock_query_side_effect(model):
        if model is LotGrains:
            return lot_query_mock
        elif model is Entrepot:
            return entrepot_query_mock
        elif model is Pays:
            return pays_query_mock
        elif model is Exploitation:
            return exp_query_mock
        else:
            return scalar_query_mock

    mock_session.query.side_effect = mock_query_side_effect

    result = DashboardService.get_dashboard_summary()

    assert result['metrics']['lotsStockes'] == 7
    assert result['metrics']['lotsAlerte'] == 1
    assert result['metrics']['lotsPerimes'] == 1
    assert any('datSortie' in str(call.args[0]) for call in lot_query_mock.filter.call_args_list)
    mock_session.close.assert_called_once()


@patch('services.dashboard_service.DashboardRepository.get_alertes_with_hierarchy')
def test_get_recent_alertes_success(mock_get_alertes):
    """
    SC├ëNARIO: On demande les alertes r├®centes.
    QUAND: get_recent_alertes est appel├®e.
    ALORS: Elle doit retourner une liste limit├®e d'alertes.
    """
    # --- ARRANGE ---
    mock_alertes = [{'idAlerte': 5}, {'idAlerte': 4}, {'idAlerte': 3}, {'idAlerte': 2}]
    mock_get_alertes.return_value = mock_alertes
    limit = 3

    # --- ACT ---
    result = DashboardService.get_recent_alertes(limit=limit)

    # --- ASSERT ---
    mock_get_alertes.assert_called_once()
    assert len(result) == limit
    assert result[0]['idAlerte'] == 5

@patch('services.dashboard_service.DashboardRepository.create_alerte')
def test_create_alerte_success(mock_create_alerte):
    """
    SC├ëNARIO: On cr├®e une alerte avec des donn├®es valides.
    QUAND: create_alerte est appel├®e.
    ALORS: Elle doit appeler le repository et retourner l'alerte cr├®├®e.
    """
    # --- ARRANGE ---
    alerte_data = {'idMesure': 123}
    mock_alerte = MagicMock()
    mock_alerte.to_dict.return_value = {'idAlerte': 1, 'idMesure': 123}
    mock_create_alerte.return_value = mock_alerte

    # --- ACT ---
    result = DashboardService.create_alerte(alerte_data)

    # --- ASSERT ---
    mock_create_alerte.assert_called_once_with({'idMesure': 123})
    assert result['idAlerte'] == 1

@patch('services.dashboard_service.commit_session')
@patch('services.dashboard_service.get_db')
def test_update_alerte_statut_success(mock_get_db, mock_commit):
    """
    SC├ëNARIO: On met ├á jour le statut d'une alerte existante.
    QUAND: update_alerte_statut est appel├®e.
    ALORS: La session doit ├¬tre commit├®e.
    """
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_alerte = MagicMock()
    mock_alerte.to_dict.return_value = {'idAlerte': 1}
    
    mock_session.query.return_value.filter.return_value.first.return_value = mock_alerte
    
    # --- ACT ---
    result = DashboardService.update_alerte_statut(1, 'traitee')

    # --- ASSERT ---
    mock_commit.assert_called_once()
    assert result is not None
    mock_session.close.assert_called_once()

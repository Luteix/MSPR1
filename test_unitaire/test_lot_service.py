import pytest
from unittest.mock import patch, MagicMock
from services.lot_service import LotService
from datetime import datetime, timedelta, UTC
from models import StatutLot

# =============================================================================
# TESTS POUR LotService
# =============================================================================

@patch('services.lot_service.get_db')
def test_get_all_lots_success(mock_get_db):
    """
    SC├ëNARIO: On demande la liste de tous les lots.
    QUAND: get_all_lots est appel├®e.
    ALORS: Elle doit retourner la liste des lots existants.
    """
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_lot1 = MagicMock()
    mock_lot1.to_dict.return_value = {'idLotGrains': 1}
    mock_lot2 = MagicMock()
    mock_lot2.to_dict.return_value = {'idLotGrains': 2}
    
    # Simuler la cha├«ne SQLAlchemy: session.query().options().order_by().all()
    mock_session.query.return_value.options.return_value.order_by.return_value.all.return_value = [mock_lot1, mock_lot2]

    # --- ACT ---
    result = LotService.get_all_lots()

    # --- ASSERT ---
    mock_get_db.assert_called_once()
    assert len(result) == 2
    assert result[0]['idLotGrains'] == 1
    assert result[1]['idLotGrains'] == 2
    mock_session.close.assert_called_once()

@patch('services.lot_service.get_db')
def test_get_lot_by_id_success(mock_get_db):
    """
    SC├ëNARIO: On demande un lot sp├®cifique avec un ID valide.
    QUAND: get_lot_by_id est appel├®e.
    ALORS: Elle doit retourner le lot correspondant.
    """
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_lot = MagicMock()
    mock_lot.to_dict.return_value = {'idLotGrains': 1, 'idEntrepot': 1}
    
    # Simuler: session.query().options().filter().first()
    mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_lot

    # --- ACT ---
    result = LotService.get_lot_by_id(1)

    # --- ASSERT ---
    assert result is not None
    assert result['idLotGrains'] == 1
    mock_session.close.assert_called_once()

@patch('services.lot_service.get_db')
def test_get_lot_by_id_not_found(mock_get_db):
    """
    SC├ëNARIO: On demande un lot qui n'existe pas.
    QUAND: get_lot_by_id est appel├®e.
    ALORS: Elle doit retourner None.
    """
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    # Simuler un retour vide
    mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = None

    # --- ACT ---
    result = LotService.get_lot_by_id(999)

    # --- ASSERT ---
    assert result is None
    mock_session.close.assert_called_once()

@patch('services.lot_service.commit_session')
@patch('services.lot_service.get_db')
def test_update_lot_success(mock_get_db, mock_commit_session):
    """
    SC├ëNARIO: On met ├á jour les informations d'un lot.
    QUAND: update_lot est appel├®e avec de nouvelles donn├®es.
    ALORS: Elle doit appeler la session et retourner le lot modifi├®.
    """
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_lot = MagicMock()
    mock_lot.to_dict.return_value = {'idLotGrains': 1, 'datSortie': '2024-05-21T10:00:00+00:00'}
    
    mock_session.query.return_value.filter.return_value.first.return_value = mock_lot

    update_data = {'datSortie': '2024-05-21T10:00:00Z'}

    # --- ACT ---
    result = LotService.update_lot(1, update_data)

    # --- ASSERT ---
    mock_commit_session.assert_called_once()
    assert result['datSortie'] == '2024-05-21T10:00:00+00:00'
    mock_session.close.assert_called_once()

@patch('services.lot_service.get_db')
def test_get_alertes_by_lot_success(mock_get_db):
    """
    SC├ëNARIO: On demande l'historique des alertes pour un lot.
    QUAND: get_alertes_by_lot est appel├®e.
    ALORS: Elle doit retourner la liste des alertes.
    """
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_lot = MagicMock()
    mock_lot.datSto = datetime(2024, 1, 1)
    mock_lot.datSortie = None
    mock_lot.idEntrepot = 1
    
    mock_alerte = MagicMock()
    mock_alerte.to_dict.return_value = {'idAlerte': 1, 'type': 'Temp├®rature'}
    
    def mock_query_side_effect(model):
        query_mock = MagicMock()
        if model.__name__ == 'LotGrains':
            query_mock.filter.return_value.first.return_value = mock_lot
        elif model.__name__ == 'Alerte':
            query_mock.join.return_value.filter.return_value.options.return_value.order_by.return_value.all.return_value = [mock_alerte]
        return query_mock
        
    mock_session.query.side_effect = mock_query_side_effect

    # --- ACT ---
    result = LotService.get_alertes_by_lot(1)

    # --- ASSERT ---
    assert len(result) == 1
    assert result[0]['idAlerte'] == 1
    mock_session.close.assert_called_once()

@patch('services.lot_service.commit_session')
@patch('services.lot_service.get_db')
def test_update_lot_status_changes_status_to_perime(mock_get_db, mock_commit):
    """
    SC├ëNARIO: Un lot est stock├® depuis plus de 365 jours.
    QUAND: update_lot_status est appel├®e.
    ALORS: Le statut du lot doit devenir 'p├®rim├®'.
    """
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session

    # Cr├®er un mock pour le lot
    mock_lot = MagicMock()
    mock_lot.statut = StatutLot.CONFORME.value
    mock_lot.datSto = datetime.now(UTC) - timedelta(days=400) # P├®rim├®
    # Simuler la hi├®rarchie pour que la 2e partie de _calculer_statut_lot ne soit pas ex├®cut├®e
    mock_lot.entrepot.exploitation.pays = None

    # La requ├¬te doit retourner ce lot
    mock_session.query.return_value.options.return_value.all.return_value = [mock_lot]

    # --- ACT ---
    LotService.update_lot_status()

    # --- ASSERT ---
    # Le statut a bien ├®t├® modifi├® sur l'objet mock
    assert mock_lot.statut == StatutLot.PERIME.value
    # La session a ├®t├® commit
    mock_commit.assert_called_once()
    # La session a ├®t├® ferm├®e
    mock_session.close.assert_called_once()

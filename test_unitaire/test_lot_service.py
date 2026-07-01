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
    # Récupère la liste complète des lots triés
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_lot1 = MagicMock()
    mock_lot1.to_dict.return_value = {'idLotGrains': 1}
    mock_lot2 = MagicMock()
    mock_lot2.to_dict.return_value = {'idLotGrains': 2}
    
    # Simule la chaine SQLAlchemy: query().options().order_by().all()
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
    # Récupère un lot existant par son ID
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_lot = MagicMock()
    mock_lot.to_dict.return_value = {'idLotGrains': 1, 'idEntrepot': 1}
    
    # Simule: query().options().filter().first()
    mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_lot

    # --- ACT ---
    result = LotService.get_lot_by_id(1)

    # --- ASSERT ---
    assert result is not None
    assert result['idLotGrains'] == 1
    mock_session.close.assert_called_once()

@patch('services.lot_service.get_db')
def test_get_lot_by_id_not_found(mock_get_db):
    # Retourne None si le lot n'existe pas
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    # Simule un retour vide
    mock_session.query.return_value.options.return_value.filter.return_value.first.return_value = None

    # --- ACT ---
    result = LotService.get_lot_by_id(999)

    # --- ASSERT ---
    assert result is None
    mock_session.close.assert_called_once()

@patch('services.lot_service.commit_session')
@patch('services.lot_service.get_db')
def test_update_lot_success(mock_get_db, mock_commit_session):
    # Met à jour un lot (ex: date de sortie) et change son statut à 'vendu'
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
    assert mock_lot.statut == 'vendu'
    mock_session.close.assert_called_once()

@patch('services.lot_service.get_db')
def test_get_alertes_by_lot_success(mock_get_db):
    # Récupère l'historique des alertes associées à un lot
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_lot = MagicMock()
    mock_lot.datSto = datetime(2024, 1, 1)
    mock_lot.datSortie = None
    mock_lot.idEntrepot = 1
    
    mock_alerte = MagicMock()
    mock_alerte.to_dict.return_value = {'idAlerte': 1, 'type': 'Température'}
    
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
    # Marque un lot comme 'périmé' s'il dépasse 365 jours de stockage
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session

    # Créer un mock pour le lot
    mock_lot = MagicMock()
    mock_lot.statut = StatutLot.CONFORME.value
    mock_lot.datSto = datetime.now(UTC) - timedelta(days=400) # P├®rim├®
    mock_lot.datSortie = None
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

@patch('services.lot_service.commit_session')
@patch('services.lot_service.get_db')
def test_update_lot_status_keeps_vendu(mock_get_db, mock_commit):
    # SCÉNARIO: Un lot vendu a une date de sortie.
    # QUAND: update_lot_status est appelée.
    # ALORS: Le statut reste 'vendu' et n'est pas recalculé.
    # --- ARRANGE ---
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session

    mock_lot = MagicMock()
    mock_lot.datSortie = datetime.now(UTC) - timedelta(days=10)
    mock_lot.statut = StatutLot.EN_ALERTE.value
    mock_lot.entrepot.exploitation.pays = None

    mock_session.query.return_value.options.return_value.all.return_value = [mock_lot]

    # --- ACT ---
    LotService.update_lot_status()

    # --- ASSERT ---
    assert mock_lot.statut == StatutLot.VENDU.value
    mock_commit.assert_called_once()
    mock_session.close.assert_called_once()

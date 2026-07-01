import pytest
from unittest.mock import patch, MagicMock
from services.entrepot_service import EntrepotService

# =============================================================================
# TESTS POUR EntrepotService
# =============================================================================

@patch('services.entrepot_service.EntrepotRepository.get_all')
def test_get_all_entrepots(mock_get_all):
    # Vérifie que le service retourne bien la liste des entrepôts du repo
    mock_get_all.return_value = [MagicMock(), MagicMock()]
    result = EntrepotService.get_all_entrepots()
    mock_get_all.assert_called_once()
    assert len(result) == 2

@patch('services.entrepot_service.EntrepotRepository.get_by_id')
def test_get_entrepot_by_id_success(mock_get_by_id):
    # Cas nominal: récupère un entrepôt par son ID
    mock_entrepot = MagicMock()
    mock_get_by_id.return_value = mock_entrepot
    result = EntrepotService.get_entrepot_by_id(1)
    mock_get_by_id.assert_called_once_with(1)
    assert result == mock_entrepot

@patch('services.entrepot_service.EntrepotRepository.get_by_id')
def test_get_entrepot_by_id_not_found(mock_get_by_id):
    # Cas erreur: lève une exception si l'entrepôt n'existe pas
    mock_get_by_id.return_value = None
    with pytest.raises(ValueError, match='Entrepot non trouvé'):
        EntrepotService.get_entrepot_by_id(999)

@patch('services.entrepot_service.get_db')
def test_get_mesures_by_entrepot(mock_get_db):
    # Récupère les mesures enregistrées pour un entrepôt donné
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    mock_mesure = MagicMock()
    mock_mesure.to_dict.return_value = {'idMesure': 1}
    mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_mesure]
    
    result = EntrepotService.get_mesures_by_entrepot(1)
    
    assert len(result) == 1
    assert result[0]['idMesure'] == 1
    mock_session.close.assert_called_once()

@patch('services.entrepot_service.get_db')
def test_get_lots_by_entrepot(mock_get_db):
    # Récupère les lots stockés dans un entrepôt
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    mock_lot = MagicMock()
    mock_lot.to_dict.return_value = {'idLotGrains': 1}
    mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_lot]
    
    result = EntrepotService.get_lots_by_entrepot(1)
    
    assert len(result) == 1
    assert result[0]['idLotGrains'] == 1
    mock_session.close.assert_called_once()

@patch('services.entrepot_service.commit_session')
@patch('services.entrepot_service.get_db')
def test_create_lot_in_entrepot_success(mock_get_db, mock_commit):
    # Crée un lot dans un entrepôt et valide la sauvegarde DB
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = MagicMock()
    
    mock_lot = MagicMock()
    mock_lot.to_dict.return_value = {'idLotGrains': 1}
    
    with patch('services.entrepot_service.LotGrains', return_value=mock_lot) as mock_LotGrains_class:
        data = {'datSto': '2024-01-01T00:00:00Z'}
        result = EntrepotService.create_lot_in_entrepot(1, data)
        
        mock_LotGrains_class.assert_called_once()
        mock_session.add.assert_called_once_with(mock_lot)
        mock_commit.assert_called_once()
        assert result['idLotGrains'] == 1
        mock_session.close.assert_called_once()

@patch('services.entrepot_service.commit_session')
@patch('services.entrepot_service.get_db')
def test_create_entrepot(mock_get_db, mock_commit):
    # Crée un nouvel entrepôt avec validation des champs requis
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    mock_entrepot = MagicMock()
    mock_entrepot.to_dict.return_value = {'idEntrepot': 1}
    with patch('services.entrepot_service.Entrepot', return_value=mock_entrepot) as mock_Entrepot_class:
        data = {'idExploitation': 1, 'nom': 'Test', 'adresse': '123 rue', 'limiteQte': 1000}
        result = EntrepotService.create_entrepot(data)
        mock_Entrepot_class.assert_called_once_with(**data)
        mock_session.add.assert_called_once_with(mock_entrepot)
        mock_commit.assert_called_once()
        assert result['idEntrepot'] == 1
        mock_session.close.assert_called_once()

@patch('services.entrepot_service.commit_session')
@patch('services.entrepot_service.get_db')
def test_update_entrepot(mock_get_db, mock_commit):
    # Modifie les informations d'un entrepôt existant
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    mock_entrepot = MagicMock()
    mock_entrepot.to_dict.return_value = {'idEntrepot': 1, 'nom': 'Nouveau Nom'}
    mock_session.query.return_value.filter.return_value.first.return_value = mock_entrepot
    
    data = {'nom': 'Nouveau Nom'}
    result = EntrepotService.update_entrepot(1, data)
    
    assert mock_entrepot.nom == 'Nouveau Nom'
    mock_commit.assert_called_once()
    assert result['nom'] == 'Nouveau Nom'
    mock_session.close.assert_called_once()

@patch('services.entrepot_service.commit_session')
@patch('services.entrepot_service.get_db')
def test_delete_entrepot(mock_get_db, mock_commit):
    # Supprime un entrepôt de la DB
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    mock_entrepot = MagicMock()
    mock_session.query.return_value.filter.return_value.first.return_value = mock_entrepot
    
    result = EntrepotService.delete_entrepot(1)
    
    mock_session.delete.assert_called_once_with(mock_entrepot)
    mock_commit.assert_called_once()
    assert result is True
    mock_session.close.assert_called_once()

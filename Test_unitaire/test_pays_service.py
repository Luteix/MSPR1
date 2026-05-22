import pytest
from unittest.mock import patch, MagicMock
from services.pays_service import PaysService
from models import Exploitation, Entrepot, LotGrains

# =============================================================================
# TESTS POUR PaysService
# =============================================================================

@patch('services.pays_service.get_db')
def test_get_all_pays(mock_get_db):
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    mock_pays = MagicMock()
    mock_pays.to_dict.return_value = {'idPays': 1, 'nom': 'France'}
    mock_session.query.return_value.all.return_value = [mock_pays]
    
    result = PaysService.get_all_pays()
    
    assert len(result) == 1
    assert result[0]['nom'] == 'France'
    mock_session.close.assert_called_once()

@patch('services.pays_service.get_db')
def test_get_pays_by_id_success(mock_get_db):
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    mock_pays = MagicMock()
    mock_pays.to_dict.return_value = {'idPays': 1, 'nom': 'France'}
    mock_session.query.return_value.filter.return_value.first.return_value = mock_pays
    
    result = PaysService.get_pays_by_id(1)
    
    assert result['nom'] == 'France'
    mock_session.close.assert_called_once()

@patch('services.pays_service.get_db')
def test_get_pays_by_id_not_found(mock_get_db):
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    result = PaysService.get_pays_by_id(999)
    
    assert result is None
    mock_session.close.assert_called_once()

@patch('services.pays_service.get_db')
def test_get_exploitations_by_pays(mock_get_db):
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_exp = MagicMock()
    mock_exp.idExploitation = 1
    mock_exp.idPays = 1
    mock_exp.nom = 'Exploitation 1'
    
    exp_query_mock = MagicMock()
    exp_query_mock.filter.return_value.all.return_value = [mock_exp]
    
    entrepot_query_mock = MagicMock()
    entrepot_query_mock.filter.return_value.count.return_value = 2
    
    lot_query_mock = MagicMock()
    lot_filter_mock = MagicMock()
    lot_filter_mock.count.side_effect = [10, 0, 1] # 10 lots, 0 périmé, 1 alerte
    lot_query_mock.join.return_value.filter.return_value = lot_filter_mock
    
    def mock_query_side_effect(model):
        if model is Exploitation:
            return exp_query_mock
        elif model is Entrepot:
            return entrepot_query_mock
        elif model is LotGrains:
            return lot_query_mock
        return MagicMock()
    
    mock_session.query.side_effect = mock_query_side_effect
    
    result = PaysService.get_exploitations_by_pays(1)
    
    assert len(result) == 1
    assert result[0]['nom'] == 'Exploitation 1'
    assert result[0]['nbEntrepots'] == 2
    assert result[0]['nbLots'] == 10
    assert result[0]['statutGlobal'] == 'en alerte'
    mock_session.close.assert_called_once()

@patch('services.pays_service.get_db')
def test_get_mesures_history(mock_get_db):
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_mesure = MagicMock()
    mock_mesure.date.strftime.return_value = '2024-05-21'
    mock_mesure.avgTemp = 22.5
    
    # Simule l'appel complexe : func.date(...), func.avg(...)
    mock_session.query.return_value.join.return_value.join.return_value.filter.return_value.group_by.return_value.all.return_value = [mock_mesure]
    
    result = PaysService.get_mesures_history(1)
    
    assert len(result) == 1
    assert result[0]['date'] == '2024-05-21'
    assert result[0]['avgTemp'] == 22.5
    mock_session.close.assert_called_once()

@patch('services.pays_service.commit_session')
@patch('services.pays_service.get_db')
def test_create_pays(mock_get_db, mock_commit):
    mock_session = MagicMock()
    mock_get_db.return_value = mock_session
    
    mock_pays = MagicMock()
    mock_pays.to_dict.return_value = {'idPays': 1, 'nom': 'Brésil'}
    
    with patch('services.pays_service.Pays', return_value=mock_pays):
        data = {
            'nom': 'Brésil',
            'temperatureMin': 15,
            'temperatureMax': 25,
            'humiditeMin': 50,
            'humiditeMax': 70
        }
        result = PaysService.create_pays(data)
        
        mock_session.add.assert_called_once_with(mock_pays)
        mock_commit.assert_called_once()
        assert result['nom'] == 'Brésil'
        mock_session.close.assert_called_once()
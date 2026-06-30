USE futurekawa;

-- 1. Insertion du pays Brésil uniquement
INSERT INTO Pays (idPays, nom, temperatureMin, temperatureMax, humiditeMin, humiditeMax) VALUES
(1, 'Brésil', 18.50, 34.00, 60.00, 92.00);

-- 2. Insertion d'exploitations brésiliennes variées
INSERT INTO Exploitations (idExploitation, nom, idPays) VALUES
(1, 'Fazenda Santa Maria', 1),
(2, 'Rancho Rio Doce', 1),
(3, 'Serra do Café', 1),
(4, 'Ouro Verde', 1),
(5, 'Bahia Coffee', 1),
(6, 'Minas Garden', 1);

-- 3. Insertion d'entrepôts liés au Brésil
INSERT INTO Entrepots (idEntrepot, nom, adresse, limiteQte, idExploitation) VALUES
(1, 'Hangar A1', 'Rua 10, Santos', 5000, 1),
(2, 'Silo Central', 'Rua 15, Santos', 10000, 1),
(3, 'Stock Sud', 'Av. Brasil, Vitória', 3000, 2),
(4, 'Nord Storage', 'Av. Brasil, Vitória', 3000, 2),
(5, 'Armazém Alpha', 'Rua das Acácias, Belo Horizonte', 4500, 3),
(6, 'Silo Principal', 'Rua das Palmeiras, Belo Horizonte', 8000, 3),
(7, 'Depósito Norte', 'Av. Paulista, São Paulo', 6000, 4),
(8, 'Café Premium', 'Rua da Aurora, Salvador', 7000, 5),
(9, 'Petit Entrepôt', 'Rua do Sol, Feira de Santana', 1500, 5),
(10, 'Armazém 5', 'Av. do Cerrado, Cuiabá', 2000, 6),
(11, 'Stock 11', 'Rua do Ouro, Juiz de Fora', 2500, 6);

-- 4. Insertion d'utilisateurs brésiliens
INSERT INTO Utilisateurs (idUtilisateur, nom, prenom, mail, mdp, idExploitation, idPoste) VALUES
(1, 'Silva', 'Maria', 'maria@kawa.com', 'hash123', 1, 2),
(2, 'Pereira', 'Lucas', 'lucas@kawa.com', 'hash123', 1, 1),
(3, 'Costa', 'Ana', 'ana@kawa.com', 'hash123', 2, 1),
(4, 'Souza', 'Pedro', 'pedro@kawa.com', 'hash123', 2, 1),
(5, 'Rocha', 'Juliana', 'juliana@kawa.com', 'hash123', 3, 1),
(6, 'Alves', 'Mateus', 'mateus@kawa.com', 'hash123', 3, 1),
(7, 'Mendes', 'Beatriz', 'beatriz@kawa.com', 'hash123', 4, 1),
(8, 'Nunes', 'Rafael', 'rafael@kawa.com', 'hash123', 4, 1),
(9, 'Barbosa', 'Sofia', 'sofia@kawa.com', 'hash123', 5, 1),
(10, 'Teixeira', 'Diego', 'diego@kawa.com', 'hash123', 6, 1);

-- 5. Insertion de mesures réalistes pour le Brésil
INSERT INTO Mesures (idMesure, temperature, humidite, datMesure, idEntrepot) VALUES
(1, 24.5, 70.2, '2024-03-20 10:00:00', 1),
(2, 45.0, 95.0, '2024-03-20 10:05:00', 1),
(3, 22.1, 65.5, '2024-03-20 10:00:00', 2),
(4, 21.8, 64.0, '2024-03-20 10:30:00', 2),
(5, 19.5, 58.2, '2024-03-20 11:00:00', 5),
(6, 19.8, 59.0, '2024-03-20 11:15:00', 5),
(7, 14.2, 52.0, '2024-03-20 12:00:00', 8),
(8, 5.0, 30.0, '2024-03-20 12:05:00', 8),
(9, 20.0, 60.0, '2024-03-20 09:00:00', 3),
(10, 20.2, 60.5, '2024-03-20 10:00:00', 4),
(11, 21.0, 61.0, '2024-03-20 11:00:00', 6),
(12, 22.0, 62.0, '2024-03-20 12:00:00', 7);

-- 6. Insertion d'alertes liées aux mesures critiques
INSERT INTO Alertes (idMesure) VALUES
(2),
(8),
(11);

-- 7. Insertion de lots de grains liés à des entrepôts brésiliens
INSERT INTO LotGrains (idLotGrains, datSto, statut, datSortie, idEntrepot) VALUES
(1, '2024-01-10', 'Stocké', NULL, 1),
(2, '2024-01-12', 'Vendu', '2024-02-15', 1),
(3, '2024-02-01', 'Stocké', NULL, 2),
(4, '2024-02-05', 'Transit', NULL, 5),
(5, '2024-01-20', 'Stocké', NULL, 8),
(6, '2024-01-25', 'Vendu', '2024-03-01', 8),
(7, '2024-03-01', 'Stocké', NULL, 3),
(8, '2024-03-02', 'Stocké', NULL, 4),
(9, '2024-03-03', 'Stocké', NULL, 6),
(10, '2024-03-04', 'Stocké', NULL, 7);
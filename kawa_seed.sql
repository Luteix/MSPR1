USE futureKawa;

-- 1. Insertion des PAYS (3 pays imposés)
INSERT INTO Pays (idPays, nom, temperatureMin, temperatureMax, humiditeMin, humiditeMax) VALUES
(1, 'Brésil', 18.50, 32.00, 60.00, 90.00),
(2, 'Colombie', 15.00, 28.00, 55.00, 85.00),
(3, 'Équateur', 12.00, 25.00, 50.00, 80.00);

-- 2. Insertion des EXPLOITATIONS (6 par pays approx.)
INSERT INTO Exploitation (idExploitation, nom, idPays) VALUES
(1, 'Fazenda Santa Maria', 1), (2, 'Rancho Rio Doce', 1), (3, 'Serra do Cafe', 1), (4, 'Ouro Verde', 1), (5, 'Bahia Coffee', 1), (6, 'Minas Garden', 1),
(7, 'Finca La Esperanza', 2), (8, 'El Mirador', 2), (9, 'Cafetal Medellin', 2), (10, 'Sierra Nevada', 2), (11, 'Huila Heights', 2), (12, 'Andes Aroma', 2),
(13, 'Amazonia Viva', 3), (14, 'Volcan Pichincha', 3), (15, 'Mitad del Mundo', 3), (16, 'Galapagos Beans', 3), (17, 'Quito Roast', 3), (18, 'Sol de Ecuador', 3);

-- 3. Insertion des ENTREPOTS (1 à 2 par exploitation)
INSERT INTO Entrepot (idEntrepot, nom, adresse, limiteQte, idExploitation) VALUES
(1, 'Hangar A1', 'Rua 10, Santos', 5000, 1), (2, 'Silo Central', 'Rua 15, Santos', 10000, 1),
(3, 'Stock Sud', 'Av. Brasil, Vitoria', 3000, 2), (4, 'Nord Storage', 'Av. Brasil, Vitoria', 3000, 2),
(5, 'Warehouse Alpha', 'Calle 5, Bogota', 4500, 7), (6, 'Silo Principal', 'Calle 8, Bogota', 8000, 7),
(7, 'Deposito Norte', 'Carrera 12, Cali', 6000, 8), (8, 'Ecuador Main', 'Av. de los Shyris, Quito', 7000, 13),
(9, 'Petit Entrepot', 'Rue de la Paix, Quito', 1500, 14), (10, 'Magasin 5', 'Quito Sector 4', 2000, 15),
(11, 'Stock 11', 'Lieu-dit 1', 2500, 3), (12, 'Stock 12', 'Lieu-dit 2', 2500, 4), (13, 'Stock 13', 'Lieu-dit 3', 2500, 5),
(14, 'Stock 14', 'Lieu-dit 4', 2500, 6), (15, 'Stock 15', 'Lieu-dit 5', 2500, 9), (16, 'Stock 16', 'Lieu-dit 6', 2500, 10),
(17, 'Stock 17', 'Lieu-dit 7', 2500, 11), (18, 'Stock 18', 'Lieu-dit 8', 2500, 12), (19, 'Stock 19', 'Lieu-dit 9', 2500, 16),
(20, 'Stock 20', 'Lieu-dit 10', 2500, 17);

-- 4. Insertion des UTILISATEURS (Mélange de rôles et d'exploitations)
INSERT INTO Utilisateur (idUtilisateur, nom, prenom, mail, mdp, idExploitation, idPoste) VALUES
(1, 'Dupont', 'Jean', 'jean@kawa.com', 'hash123', 1, 2),
(2, 'Silva', 'Maria', 'maria@kawa.com', 'hash123', 1, 1),
(3, 'Garcia', 'Carlos', 'carlos@kawa.com', 'hash123', 7, 2),
(4, 'Mendoza', 'Elena', 'elena@kawa.com', 'hash123', 13, 2),
(5, 'López', 'Juan', 'juan@kawa.com', 'hash123', 2, 1),
(6, 'Santos', 'Lucas', 'lucas@kawa.com', 'hash123', 3, 1),
(7, 'Ferreira', 'Ana', 'ana@kawa.com', 'hash123', 4, 1),
(8, 'Gomez', 'Luis', 'luis@kawa.com', 'hash123', 5, 1),
(9, 'Diaz', 'Sofia', 'sofia@kawa.com', 'hash123', 6, 1),
(10, 'Torres', 'Diego', 'diego@kawa.com', 'hash123', 8, 1),
(11, 'Ruiz', 'Carmen', 'carmen@kawa.com', 'hash123', 9, 1),
(12, 'Morales', 'Pablo', 'pablo@kawa.com', 'hash123', 10, 1),
(13, 'Castro', 'Isabel', 'isabel@kawa.com', 'hash123', 11, 1),
(14, 'Ortiz', 'Javier', 'javier@kawa.com', 'hash123', 12, 1),
(15, 'Silva', 'Ricardo', 'ricardo@kawa.com', 'hash123', 14, 1),
(16, 'Reyes', 'Marta', 'marta@kawa.com', 'hash123', 15, 1),
(17, 'Jimenez', 'Hugo', 'hugo@kawa.com', 'hash123', 16, 1),
(18, 'Vargas', 'Laura', 'laura@kawa.com', 'hash123', 17, 1),
(19, 'Ramos', 'Oscar', 'oscar@kawa.com', 'hash123', 18, 1),
(20, 'Pereira', 'Teresa', 'teresa@kawa.com', 'hash123', 1, 1);

-- 5. Insertion des MESURES (Historique de capteurs)
INSERT INTO Mesures (idMesure, temperature, humidite, datMesure, idEntrepot) VALUES
(1, 24.5, 70.2, '2024-03-20 10:00:00', 1), (2, 45.0, 95.0, '2024-03-20 10:05:00', 1), -- Alerte potentielle ici
(3, 22.1, 65.5, '2024-03-20 10:00:00', 2), (4, 21.8, 64.0, '2024-03-20 10:30:00', 2),
(5, 19.5, 58.2, '2024-03-20 11:00:00', 5), (6, 19.8, 59.0, '2024-03-20 11:15:00', 5),
(7, 14.2, 52.0, '2024-03-20 12:00:00', 8), (8, 5.0, 30.0, '2024-03-20 12:05:00', 8), -- Alerte potentielle ici
(9, 20.0, 60.0, '2024-03-20 09:00:00', 3), (10, 20.2, 60.5, '2024-03-20 10:00:00', 4),
(11, 21.0, 61.0, '2024-03-20 11:00:00', 6), (12, 22.0, 62.0, '2024-03-20 12:00:00', 7),
(13, 23.0, 63.0, '2024-03-20 13:00:00', 9), (14, 24.0, 64.0, '2024-03-20 14:00:00', 10),
(15, 25.0, 65.0, '2024-03-20 15:00:00', 11), (16, 26.0, 66.0, '2024-03-20 16:00:00', 12),
(17, 18.0, 70.0, '2024-03-20 17:00:00', 13), (18, 19.0, 71.0, '2024-03-20 18:00:00', 14),
(19, 20.0, 72.0, '2024-03-20 19:00:00', 15), (20, 21.0, 73.0, '2024-03-20 20:00:00', 16);

-- 6. Insertion des ALERTES (Liées aux mesures critiques)
INSERT INTO Alertes (idMesure) VALUES
(2), (8), (15), (16), (20); -- Référence aux IDs de Mesures ci-dessus

-- 7. Insertion des LOTS DE GRAINS (Gestion des stocks)
INSERT INTO LotGrains (idLotGrains, datSto, statut, datSortie, idEntrepot) VALUES
(1, '2024-01-10', 'Stocké', NULL, 1), (2, '2024-01-12', 'Vendu', '2024-02-15', 1),
(3, '2024-02-01', 'Stocké', NULL, 2), (4, '2024-02-05', 'Transit', NULL, 5),
(5, '2024-01-20', 'Stocké', NULL, 8), (6, '2024-01-25', 'Vendu', '2024-03-01', 8),
(7, '2024-03-01', 'Stocké', NULL, 1), (8, '2024-03-02', 'Stocké', NULL, 3),
(9, '2024-03-03', 'Stocké', NULL, 4), (10, '2024-03-04', 'Stocké', NULL, 6),
(11, '2024-03-05', 'Stocké', NULL, 7), (12, '2024-03-06', 'Stocké', NULL, 9),
(13, '2024-03-07', 'Stocké', NULL, 10), (14, '2024-03-08', 'Stocké', NULL, 11),
(15, '2024-03-09', 'Stocké', NULL, 12), (16, '2024-03-10', 'Stocké', NULL, 13),
(17, '2024-03-11', 'Stocké', NULL, 14), (18, '2024-03-12', 'Stocké', NULL, 15),
(19, '2024-03-13', 'Stocké', NULL, 16), (20, '2024-03-14', 'Stocké', NULL, 17);
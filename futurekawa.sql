CREATE DATABASE futurekawa;
USE futureKawa;

CREATE TABLE Pays(
    idPays INT AUTO_INCREMENT,
    nom VARCHAR(50),
    temperatureMin DECIMAL(15,2),
    temperatureMax DECIMAL(15,2),
    humiditeMin DECIMAL(15,2),
    humiditeMax DECIMAL(15,2),
    PRIMARY KEY(idPays)
);

CREATE TABLE Exploitation(
    idExploitation INT AUTO_INCREMENT,
    nom VARCHAR(50),
    idPays INT NOT NULL,
    PRIMARY KEY(idExploitation),
    FOREIGN KEY(idPays) REFERENCES Pays(idPays)
);

CREATE TABLE Entrepot(
    idEntrepot INT AUTO_INCREMENT,
    nom VARCHAR(50),
    adresse VARCHAR(100),
    limiteQte INT,
    idExploitation INT NOT NULL,
    PRIMARY KEY(idEntrepot),
    FOREIGN KEY(idExploitation) REFERENCES Exploitation(idExploitation)
);

CREATE TABLE LotGrains(
    idLotGrains INT AUTO_INCREMENT,
    datSto DATE,
    statut VARCHAR(10),
    datSortie DATE,
    idEntrepot INT,
    PRIMARY KEY(idLotGrains),
    FOREIGN KEY(idEntrepot) REFERENCES Entrepot(idEntrepot)
);

CREATE TABLE Mesures(
    idMesure INT AUTO_INCREMENT,
    temperature DECIMAL(15,2),
    humidite DECIMAL(15,2),
    datMesure DATETIME,
    idEntrepot INT NOT NULL,
    PRIMARY KEY(idMesure),
    FOREIGN KEY(idEntrepot) REFERENCES Entrepot(idEntrepot)
);

CREATE TABLE Alertes(
    idAlerte INT AUTO_INCREMENT,
    idMesure INT NOT NULL,
    PRIMARY KEY(idAlerte),
    UNIQUE(idMesure),
    FOREIGN KEY(idMesure) REFERENCES Mesures(idMesure)
);

CREATE TABLE Poste(
    idPoste INT AUTO_INCREMENT,
    intitule VARCHAR(100),
    PRIMARY KEY(idPoste)
);

CREATE TABLE Utilisateur(
    idUtilisateur INT AUTO_INCREMENT,
    nom VARCHAR(50),
    prenom VARCHAR(50),
    mail VARCHAR(250),
    mdp VARCHAR(250),
    idExploitation INT NOT NULL,
    idPoste INT NOT NULL DEFAULT 1,
    PRIMARY KEY(idUtilisateur),
    FOREIGN KEY(idExploitation) REFERENCES Exploitation(idExploitation),
    FOREIGN KEY(idPoste) REFERENCES Poste(idPoste)
);

INSERT INTO Poste (intitule) VALUES
('EmployÃ©'),
('Responsable exploitation');
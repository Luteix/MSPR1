-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : jeu. 16 avr. 2026 à 09:47
-- Version du serveur : 5.7.40
-- Version de PHP : 8.0.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `futurekawa`
--

-- --------------------------------------------------------

--
-- Structure de la table `alertes`
--

DROP TABLE IF EXISTS `alertes`;
CREATE TABLE IF NOT EXISTS `alertes` (
  `idAlerte` int(11) NOT NULL AUTO_INCREMENT,
  `idMesure` int(11) NOT NULL,
  PRIMARY KEY (`idAlerte`),
  UNIQUE KEY `idMesure` (`idMesure`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `entrepot`
--

DROP TABLE IF EXISTS `entrepot`;
CREATE TABLE IF NOT EXISTS `entrepot` (
  `idEntrepot` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) DEFAULT NULL,
  `adresse` varchar(100) DEFAULT NULL,
  `limiteQte` int(11) DEFAULT NULL,
  `idExploitation` int(11) NOT NULL,
  PRIMARY KEY (`idEntrepot`),
  KEY `idExploitation` (`idExploitation`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `exploitation`
--

DROP TABLE IF EXISTS `exploitation`;
CREATE TABLE IF NOT EXISTS `exploitation` (
  `idExploitation` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) DEFAULT NULL,
  `idPays` int(11) NOT NULL,
  PRIMARY KEY (`idExploitation`),
  KEY `idPays` (`idPays`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `lotgrains`
--

DROP TABLE IF EXISTS `lotgrains`;
CREATE TABLE IF NOT EXISTS `lotgrains` (
  `idLotGrains` int(11) NOT NULL AUTO_INCREMENT,
  `datSto` date DEFAULT NULL,
  `statut` varchar(10) DEFAULT NULL,
  `datSortie` date DEFAULT NULL,
  `idEntrepot` int(11) DEFAULT NULL,
  PRIMARY KEY (`idLotGrains`),
  KEY `idEntrepot` (`idEntrepot`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `mesures`
--

DROP TABLE IF EXISTS `mesures`;
CREATE TABLE IF NOT EXISTS `mesures` (
  `idMesure` int(11) NOT NULL AUTO_INCREMENT,
  `temperature` decimal(15,2) DEFAULT NULL,
  `humidite` decimal(15,2) DEFAULT NULL,
  `datMesure` datetime DEFAULT NULL,
  `idEntrepot` int(11) NOT NULL,
  PRIMARY KEY (`idMesure`),
  KEY `idEntrepot` (`idEntrepot`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `pays`
--

DROP TABLE IF EXISTS `pays`;
CREATE TABLE IF NOT EXISTS `pays` (
  `idPays` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) DEFAULT NULL,
  `temperatureMin` decimal(15,2) DEFAULT NULL,
  `temperatureMax` decimal(15,2) DEFAULT NULL,
  `humiditeMin` decimal(15,2) DEFAULT NULL,
  `humiditeMax` decimal(15,2) DEFAULT NULL,
  PRIMARY KEY (`idPays`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `poste`
--

DROP TABLE IF EXISTS `poste`;
CREATE TABLE IF NOT EXISTS `poste` (
  `idPoste` int(11) NOT NULL AUTO_INCREMENT,
  `intitule` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`idPoste`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `poste`
--

INSERT INTO `poste` (`idPoste`, `intitule`) VALUES
(1, 'EmployÃ©'),
(2, 'Responsable exploitation');

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

DROP TABLE IF EXISTS `utilisateur`;
CREATE TABLE IF NOT EXISTS `utilisateur` (
  `idUtilisateur` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) DEFAULT NULL,
  `prenom` varchar(50) DEFAULT NULL,
  `mail` varchar(250) DEFAULT NULL,
  `mdp` varchar(250) DEFAULT NULL,
  `idExploitation` int(11) NOT NULL,
  `idPoste` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`idUtilisateur`),
  KEY `idExploitation` (`idExploitation`),
  KEY `idPoste` (`idPoste`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

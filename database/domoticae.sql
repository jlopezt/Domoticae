-- --------------------------------------------------------
-- Host:                         10.68.0.100
-- Versión del servidor:         10.3.36-MariaDB-0+deb10u2 - Raspbian 10
-- SO del servidor:              debian-linux-gnueabihf
-- HeidiSQL Versión:             12.3.0.6589
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para domoticae
CREATE DATABASE IF NOT EXISTS `domoticae` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `domoticae`;

-- Volcando estructura para tabla domoticae.Datos
CREATE TABLE IF NOT EXISTS `Datos` (
  `CID` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `SID` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `Dato` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `SSID` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `tiempo` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla domoticae.Dispositivos
CREATE TABLE IF NOT EXISTS `Dispositivos` (
  `Contrasena` varchar(32) CHARACTER SET utf8 DEFAULT NULL,
  `Validado` int(11) DEFAULT 0,
  `SID` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `CID` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `DID` varchar(16) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla domoticae.Usuarios
CREATE TABLE IF NOT EXISTS `Usuarios` (
  `Nombre` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `Apellidos` varchar(30) CHARACTER SET utf8 DEFAULT NULL,
  `Correo` varchar(30) CHARACTER SET utf8 DEFAULT NULL,
  `Telefono` varchar(9) CHARACTER SET utf8 DEFAULT NULL,
  `Usuario` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `Direccion_ppal` int(11) DEFAULT NULL,
  `Password` varchar(32) CHARACTER SET utf8 DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- La exportación de datos fue deseleccionada.

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

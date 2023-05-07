-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8mb3 ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`pacientes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`pacientes` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(25) NOT NULL,
  `apellido_pat` VARCHAR(45) NULL DEFAULT NULL,
  `apellido_mat` VARCHAR(45) NULL DEFAULT NULL,
  `correo` VARCHAR(255) NULL DEFAULT NULL,
  `password` VARCHAR(32) NOT NULL,
  `telefono` VARCHAR(10) NULL DEFAULT NULL,
  `cuidad` VARCHAR(45) NULL DEFAULT NULL,
  `sexo` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 12
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb`.`medicos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`medicos` (
  `id_m` INT NOT NULL AUTO_INCREMENT,
  `nombre_m` VARCHAR(50) NOT NULL,
  `apellido_pat_m` VARCHAR(50) NOT NULL,
  `apellido_mat_m` VARCHAR(50) NOT NULL,
  `especialidad_m` VARCHAR(255) NOT NULL,
  `telefono_m` VARCHAR(20) NOT NULL,
  `ciudad_m` VARCHAR(255) NOT NULL,
  `email_m` VARCHAR(255) NOT NULL,
  `password_m` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_m`),
  INDEX `especialidad_m` (`especialidad_m` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 9
DEFAULT CHARACTER SET = utf8mb3;


-- -----------------------------------------------------
-- Table `mydb`.`citas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`citas` (
  `id_c` INT NOT NULL AUTO_INCREMENT,
  `paciente_id` INT UNSIGNED NOT NULL,
  `medico_id` INT NOT NULL,
  `fecha` DATE NOT NULL,
  `correo` VARCHAR(255) NOT NULL,
  `motivo` VARCHAR(255) NOT NULL,
  `creado` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `tipo` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_c`),
  INDEX `medico_id` (`medico_id` ASC) VISIBLE,
  INDEX `tipo` (`tipo` ASC) VISIBLE,
  INDEX `fk_citas_pacientes` (`paciente_id` ASC) VISIBLE,
  CONSTRAINT `citas_ibfk_1`
    FOREIGN KEY (`paciente_id`)
    REFERENCES `mydb`.`pacientes` (`id`),
  CONSTRAINT `citas_ibfk_2`
    FOREIGN KEY (`medico_id`)
    REFERENCES `mydb`.`medicos` (`id_m`),
  CONSTRAINT `citas_ibfk_3`
    FOREIGN KEY (`tipo`)
    REFERENCES `mydb`.`medicos` (`especialidad_m`),
  CONSTRAINT `fk_citas_pacientes`
    FOREIGN KEY (`paciente_id`)
    REFERENCES `mydb`.`pacientes` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 10
DEFAULT CHARACTER SET = utf8mb3;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

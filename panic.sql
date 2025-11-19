CREATE DATABASE IF NOT EXISTS panic_app

USE panic_app;

CREATE TABLE IF NOT EXISTS panic_logs (
	id iNT AUTO_INCREMENT primary key,
	datetime VARCHAR(50) NOT NULL,
	note TEXT NOT NULL
);

SELECT * FROM panic_logs pl;

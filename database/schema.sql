-- Run this to set up the upgraded SQMS database

CREATE DATABASE IF NOT EXISTS sqms;
USE sqms;

CREATE TABLE IF NOT EXISTS users (
    user_id   INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(100)        NOT NULL,
    email     VARCHAR(150) UNIQUE NOT NULL,
    phone     VARCHAR(15)         NOT NULL,
    password  VARCHAR(255)        NOT NULL,   -- hashed, never plain text
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT          NOT NULL,
    hospital         VARCHAR(150) NOT NULL,
    department       VARCHAR(100) NOT NULL,
    doctor           VARCHAR(100) NOT NULL,
    appointment_date DATE         NOT NULL,
    time_slot        VARCHAR(50)  NOT NULL,
    token_number     VARCHAR(20)  NOT NULL,
    status           ENUM('Pending', 'Completed') DEFAULT 'Pending',
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
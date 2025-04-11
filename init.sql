-- Create database
CREATE DATABASE IF NOT EXISTS Hookshield;
USE Hookshield;

-- User roles table
CREATE TABLE user_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);
INSERT INTO user_roles (role_name) VALUES ('admin'), ('user');

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role_id INT NOT NULL DEFAULT 2,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    FOREIGN KEY (role_id) REFERENCES user_roles(id) ON DELETE CASCADE
);

--Email account types
CREATE TABLE email_account_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name ENUM('imap', 'Google') NOT NULL
);
INSERT INTO email_account_types (type_name) VALUES ('imap'), ('Google');

-- Email accounts table
CREATE TABLE email_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    added_by INT NOT NULL,
    account_type INT NOT NULL,
    imap_host VARCHAR(255),
    imap_password VARCHAR(255),
    token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (account_type) REFERENCES email_account_types(id) ON DELETE CASCADE
);



-- Email folders table
CREATE TABLE email_folders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name ENUM('HOOKSHIELD_SPAM','INBOX') NOT NULL
);
INSERT INTO email_folders (name) VALUES ('HOOKSHIELD_SPAM'), ('INBOX');

-- Email analyses table
CREATE TABLE email_analyses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(255) NOT NULL,
    recipient VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    receive_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_body TEXT NOT NULL,
    is_phishing BOOLEAN NOT NULL,
    blocked_date TIMESTAMP NULL,
    explanation TEXT NOT NULL,
    folder_id INT NOT NULL,
    source_email VARCHAR(255) NOT NULL,
    FOREIGN KEY (source_email) REFERENCES email_accounts(email) ON DELETE CASCADE,
    FOREIGN KEY (recipient) REFERENCES email_accounts(email) ON DELETE CASCADE,
    FOREIGN KEY (folder_id) REFERENCES email_folders(id) ON DELETE CASCADE
);

-- Admin actions log
CREATE TABLE admin_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT NOT NULL,
    action_type ENUM('add_email', 'remove_email', 'restore_email', 'add_blacklist', 'remove_blacklist', 'confirm_false_positive', 'confirm_false_negative') NOT NULL,
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    target_email VARCHAR(255),
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Reporting table for false positives/negatives
CREATE TABLE reporting (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email_id INT NOT NULL,
    report_type ENUM('false_positive', 'false_negative') NOT NULL,
    report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (email_id) REFERENCES email_analyses(id) ON DELETE CASCADE
);

-- Notifications table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    email_id INT,
    notification_type ENUM('mail_malicious_detected', 'false_positive_detected', 'false_negative_detected'),
    notification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (email_id) REFERENCES email_analyses(id) ON DELETE CASCADE
);

CREATE TABLE blacklist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    reason TEXT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    main_blacklist BOOLEAN DEFAULT FALSE,
    CONSTRAINT uix_user_email_email UNIQUE(user_email, email),
    CONSTRAINT chk_email CHECK (email LIKE '%@%.%'),
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);


-- Whitelist table
CREATE TABLE whitelist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    reason TEXT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_email CHECK (email LIKE '%@%.%')
);

-- File signatures table
CREATE TABLE file_signatures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    file_type VARCHAR(50) NOT NULL,
    email_id INT NOT NULL,
    detected_malware BOOLEAN DEFAULT FALSE,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email_id) REFERENCES email_analyses(id) ON DELETE CASCADE
);

-- Global statistics table
CREATE TABLE global_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    total_users INT DEFAULT 0,
    total_mail_analyzed INT DEFAULT 0,
    total_mail_authentic INT DEFAULT 0,
    total_mails_blocked INT DEFAULT 0,
    total_files_scanned INT DEFAULT 0,
    total_false_positive INT DEFAULT 0,
    total_false_negative INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- User statistics table
CREATE TABLE user_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_reports INT DEFAULT 0,
    mail_analyzed INT DEFAULT 0,
    mail_authentic INT DEFAULT 0,
    mails_blocked INT DEFAULT 0,
    last_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- tickets table
CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mail_uid INT NOT NULL,
    user_id INT NOT NULL,
    user_explanation TEXT NOT NULL,
    state INT DEFAULT 1,
    made_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modification_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (mail_uid) REFERENCES email_analyses(id) ON DELETE CASCADE ON UPDATE CASCADE
);



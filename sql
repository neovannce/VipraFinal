
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);





CREATE TABLE IF NOT EXISTS users_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    looking_for VARCHAR(10),
    age_min INT,
    age_max INT,
    mother_tongue VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS profiles_basic_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    profile_for VARCHAR(50),
    gender VARCHAR(10),
    first_name VARCHAR(50),
    middle_name VARCHAR(50),
    last_name VARCHAR(50),
    father_name VARCHAR(100),
    mother_name VARCHAR(100),
    dob DATE,
    age INT,
    religion VARCHAR(50),
    gotra VARCHAR(50),
    mother_tongue VARCHAR(50),
    height VARCHAR(10),
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    temp_address TEXT,
    temp_city VARCHAR(50),
    temp_district VARCHAR(50),
    temp_state VARCHAR(50),
    temp_pincode VARCHAR(10),
    perm_address TEXT,
    perm_city VARCHAR(50),
    perm_district VARCHAR(50),
    perm_state VARCHAR(50),
    perm_pincode VARCHAR(10),
    lives_with_family VARCHAR(10),
    marital_status VARCHAR(50),
    diet TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS identity_verification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    identity_type VARCHAR(100),
    identity_number VARCHAR(20),
    profile_picture VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

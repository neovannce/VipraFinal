<?php
require_once 'config/database.php';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    $sql = "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE";
    $pdo->exec($sql);
    
    echo "Column 'is_active' added successfully to users table.\n";
} catch(PDOException $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?> 
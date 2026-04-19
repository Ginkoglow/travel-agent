
-- 创建数据库
CREATE DATABASE IF NOT EXISTS travel_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE travel_agent;

-- 用户查询记录表
CREATE TABLE IF NOT EXISTS user_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_text TEXT NOT NULL,
    location VARCHAR(100),
    travel_date VARCHAR(50),
    days INT,
    preferences VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 旅行推荐结果表
CREATE TABLE IF NOT EXISTS travel_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query_id INT,
    weather_info TEXT,
    poi_info TEXT,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES user_queries(id) ON DELETE CASCADE
);
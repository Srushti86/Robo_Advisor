USE robo_advisor;

CREATE TABLE IF NOT EXISTS users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risk_profiles(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    bucket VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS portfolio_recommendations(
    id INT AUTO_INCREMENT PRIMARY KEY,
    risk_profile_id INT NOT NULL,
    weights_json JSON NOT NULL,
    sharpe_ratio FLOAT,
    sortino_ratio FLOAT,
    annualized_volatility FLOAT,
    max_drawdown FLOAT,
    diversification_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (risk_profile_id) REFERENCES risk_profiles(id) ON DELETE CASCADE
);

-- Helpful index for pulling a user's history fast
CREATE INDEX idx_risk_profiles_user ON risk_profiles(user_id);
CREATE INDEX idx_recommendations_profile ON portfolio_recommendations(risk_profile_id);
-- ==========================================================
-- Bunny Mart - MySQL data stores D1..D10 (matches the DFD)
-- ==========================================================
CREATE DATABASE IF NOT EXISTS bunny_mart CHARACTER SET utf8mb4;
USE bunny_mart;

-- D1 Users
CREATE TABLE IF NOT EXISTS users (
  user_id      INT AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,
  email        VARCHAR(150) NOT NULL UNIQUE,
  phone        VARCHAR(20),
  address      VARCHAR(255),
  password_hash VARCHAR(255) NOT NULL,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- D10 Admin
CREATE TABLE IF NOT EXISTS admin (
  admin_id     INT AUTO_INCREMENT PRIMARY KEY,
  username     VARCHAR(80) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- D3 Categories
CREATE TABLE IF NOT EXISTS categories (
  category_id  INT AUTO_INCREMENT PRIMARY KEY,
  name         VARCHAR(100) NOT NULL UNIQUE,
  description  VARCHAR(255)
) ENGINE=InnoDB;

-- D2 Products (stock column is the stock data store for process 2.4)
CREATE TABLE IF NOT EXISTS products (
  product_id   INT AUTO_INCREMENT PRIMARY KEY,
  category_id  INT,
  name         VARCHAR(150) NOT NULL,
  description  TEXT,
  price        DECIMAL(10,2) NOT NULL DEFAULT 0,
  stock        INT NOT NULL DEFAULT 0,
  image        VARCHAR(255),
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- D4 Wishlist
CREATE TABLE IF NOT EXISTS wishlist (
  wishlist_id  INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  product_id   INT NOT NULL,
  added_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_wishlist (user_id, product_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- D5 Cart
CREATE TABLE IF NOT EXISTS cart (
  cart_id      INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  product_id   INT NOT NULL,
  quantity     INT NOT NULL DEFAULT 1,
  UNIQUE KEY uq_cart (user_id, product_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- D6 Orders
CREATE TABLE IF NOT EXISTS orders (
  order_id     INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  full_name    VARCHAR(100) NOT NULL,
  phone        VARCHAR(20) NOT NULL,
  address      VARCHAR(255) NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
  status       ENUM('Pending','Confirmed','Processing','Shipped','Delivered','Cancelled') DEFAULT 'Pending',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- D7 Order Items
CREATE TABLE IF NOT EXISTS order_items (
  order_item_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id      INT NOT NULL,
  product_id    INT NOT NULL,
  quantity      INT NOT NULL,
  unit_price    DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;

-- D8 Payments
CREATE TABLE IF NOT EXISTS payments (
  payment_id    INT AUTO_INCREMENT PRIMARY KEY,
  order_id      INT NOT NULL,
  method        ENUM('COD','QR') NOT NULL,
  status        ENUM('Pending','Pending Verification','Paid','Failed') DEFAULT 'Pending',
  proof_image   VARCHAR(255),
  amount        DECIMAL(10,2) NOT NULL DEFAULT 0,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- D9 Contact Messages
CREATE TABLE IF NOT EXISTS contact_messages (
  message_id   INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NULL,
  name         VARCHAR(100) NOT NULL,
  email        VARCHAR(150) NOT NULL,
  subject      VARCHAR(150),
  message      TEXT NOT NULL,
  admin_reply  TEXT,
  status       ENUM('New','Read','Responded') DEFAULT 'New',
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Seed categories
INSERT IGNORE INTO categories (name, description) VALUES
 ('Aquarium Fish', 'Freshwater and tropical fish'),
 ('Pets', 'Small pets and companions'),
 ('Fish Food', 'Pellets, flakes and live food'),
 ('Accessories', 'Tanks, filters, decorations');

-- ==========================================================
-- PAYMENT QR SETTINGS
-- Admin controlled active UPI QR code
-- ==========================================================

CREATE TABLE IF NOT EXISTS payment_qr_settings (
  qr_id         INT AUTO_INCREMENT PRIMARY KEY,
  qr_image      VARCHAR(255) NOT NULL,
  account_name  VARCHAR(100),
  bank_name     VARCHAR(100),
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- D11 Payment QR Settings
CREATE TABLE IF NOT EXISTS payment_qr (
  qr_id        INT AUTO_INCREMENT PRIMARY KEY,
  qr_image     VARCHAR(255) NOT NULL,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
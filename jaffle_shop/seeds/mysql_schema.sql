CREATE DATABASE IF NOT EXISTS jaffle_shop;
USE jaffle_shop;

SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS raw_customers;
CREATE TABLE raw_customers (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  first_name varchar(255),
  last_name varchar(255)
);

DROP TABLE IF EXISTS raw_orders;
CREATE TABLE raw_orders (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  status varchar(255), #ENUM('completed', 'returned', 'return_pending', 'shipped', 'placed'),
  order_date DATE,
  
  FOREIGN KEY (user_id) REFERENCES raw_customers(id),
  KEY (`user_id`, `status`)
);

DROP TABLE IF EXISTS raw_payments;
CREATE TABLE raw_payments (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  payment_method varchar(255), #ENUM('credit_card', 'coupon', 'bank_transfer', 'gift_card'),
  amount INT,

  FOREIGN KEY (order_id) REFERENCES raw_orders(id),
  KEY (`order_id`, `payment_method`)
);

SET FOREIGN_KEY_CHECKS=1;

SET global local_infile=1;
LOAD DATA LOCAL INFILE 'raw_customers.csv' INTO TABLE raw_customers FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'raw_orders.csv' INTO TABLE raw_orders FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'raw_payments.csv' INTO TABLE raw_payments FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES;

# We also make it an enum (for some reason if the table defn is enum the values don't load, so we fix it up here)
ALTER TABLE raw_orders MODIFY COLUMN status ENUM('completed', 'returned', 'return_pending', 'shipped', 'placed');
ALTER TABLE raw_payments MODIFY COLUMN payment_method ENUM('credit_card', 'coupon', 'bank_transfer', 'gift_card');





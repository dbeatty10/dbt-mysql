This is an example repo of the dbt-mysql driver here: https://github.com/dbeatty10/dbt-mysql

Start by setting up your local test database mysql data:

```
$ cd seeds
$ cat mysql_schema.sql | mysql -uroot
$ cd ..
```

This will create the dbt_jaffle_shop database for you. You can view the data with:

```
mysql -uroot -e "SELECT * FROM jaffle_shop.raw_customers;"
mysql -uroot -e "SELECT * FROM jaffle_shop.raw_orders;"
mysql -uroot -e "SELECT * FROM jaffle_shop.raw_payments;"
```


To get setup make your virtualenv and install the requirements: `pip install -r requirements.txt`


Then you can setup $HOME/.dbt/profiles.yml:

```
jaffle_shop:
  target: dev
  outputs:
    dev:
      type: mysql
      server: 127.0.0.1
      port: 3306  # optional
      database: dbt_jaffle_shop # optional, should be same as schema
      schema: dbt_jaffle_shop
      username: root
      password:
      driver: MySQL ODBC 8.0 ANSI Driver
```

Now run dbt:

```
dbt run
```

The output views will go into the MySQL database called dbt_jaffle_shop.

```
mysql -uroot -e "SELECT * FROM dbt_jaffle_shop.stg_customers;"
mysql -uroot -e "SELECT * FROM dbt_jaffle_shop.stg_orders;"
mysql -uroot -e "SELECT * FROM dbt_jaffle_shop.stg_payments;"
mysql -uroot -e "SELECT * FROM dbt_jaffle_shop.customers;"
mysql -uroot -e "SELECT * FROM dbt_jaffle_shop.orders;"
```

Finally:

```
dbt docs
dbt docs serve --port 8001
```

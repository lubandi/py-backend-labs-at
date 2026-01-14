"""
Data Seeding Module for E-Commerce Analytics Pipeline

This module is responsible for:
1. Initializing the database schema
2. Generating a large, realistic dataset for demonstration
3. Creating customers, products, orders, and order items
4. Ensuring sufficient data volume for meaningful analytics and index performance
"""

import os
import random
import traceback

from e_commerce_analytics_data_pipeline.database.db import db
from e_commerce_analytics_data_pipeline.models import Customer, Product
from e_commerce_analytics_data_pipeline.operations import EcommerceOperations
from faker import Faker

fake = Faker()


def init_db():
    """
    Initialize the database by creating all tables from the schema.sql file.

    This function:
    1. Locates the schema.sql file (checks both relative paths)
    2. Reads the SQL schema definition
    3. Executes the schema creation statements
    4. Creates tables for customers, products, orders, and order_items

    Raises:
        FileNotFoundError: If schema.sql cannot be found
        Exception: For any database connection or execution errors
    """
    print("Initializing Database with Schema...")
    schema_path = os.path.join("sql", "schema.sql")
    if not os.path.exists(schema_path):
        schema_path = os.path.join("..", "sql", "schema.sql")

    with open(schema_path, "r") as f:
        schema_sql = f.read()

    with db.get_cursor() as cursor:
        cursor.execute(schema_sql)
    print("Database Initialized.")


def seed_data():
    """
    Generate and populate a large dataset for e-commerce analytics demonstration.

    This function creates:
    1. 100 unique customers with realistic names and emails
    2. 200 products with diverse categories and rich JSON metadata
    3. 2200+ orders to ensure meaningful analytics and index performance
    4. 3700+ order items linking products to orders

    The dataset is specifically sized to:
    - Demonstrate clear performance improvements with indexes
    - Provide sufficient data for complex analytics queries
    - Show realistic e-commerce patterns and distributions

    Note:
        Uses a hybrid approach for order creation:
        - First 200 orders: Created transactionally to demonstrate ACID properties
        - Remaining 2000 orders: Bulk-inserted for performance

    Returns:
        None, but prints progress and summary statistics
    """
    print("Seeding Data...")

    # 1. Customers - Create 100 unique customers
    customer_ids = []
    print(" Creating 100 Customers...")
    for _ in range(100):
        c = Customer(name=fake.name(), email=fake.unique.email())
        cid = EcommerceOperations.add_customer(c)
        customer_ids.append(cid)
    print(f"✓ Created {len(customer_ids)} customers")

    # 2. Products - Create 200 diverse products with JSON metadata
    product_ids = []
    categories = ["Electronics", "Books", "Clothing", "Home", "Toys"]
    print(" Creating 200 Products...")
    for _ in range(200):
        cat = random.choice(categories)
        meta = {
            "color": fake.color_name(),
            "material": fake.word(),
            "rating": random.randint(1, 5),
        }
        p = Product(
            name=fake.catch_phrase(),
            category=cat,
            price=round(random.uniform(10.0, 500.0), 2),
            stock_quantity=random.randint(100, 500),
            metadata=meta,
        )
        pid = EcommerceOperations.add_product(p)
        product_ids.append(pid)
    print(f"✓ Created {len(product_ids)} products")

    # 3. Orders - Create 2200+ orders for meaningful analytics
    print(" Creating 2000+ Orders...")
    orders_created = 0

    # First create 200 orders using transactional method (demonstrates ACID)
    for _ in range(200):
        cid = random.choice(customer_ids)
        items = []
        num_items = random.randint(1, 4)
        selected_pids = random.sample(product_ids, num_items)
        for pid in selected_pids:
            items.append({"product_id": pid, "quantity": random.randint(1, 3)})

        try:
            EcommerceOperations.create_order(cid, items)
            orders_created += 1
            if orders_created % 50 == 0:
                print(f"  Created {orders_created} orders...")
        except ValueError as e:
            # Skip if order faile it's stock issues
            print(f"Skipping due to: {e}")

            continue

    # Bulk insert 2000 more orders for performance (non-transactional)
    print(" Bulk inserting 2000 more orders...")
    with db.get_cursor() as cursor:
        # Get all customer IDs for random assignment
        cursor.execute("SELECT customer_id FROM customers")
        all_customer_ids = [row[0] for row in cursor.fetchall()]

        # Insert 2000 orders with random customers and amounts
        for i in range(2000):
            cid = random.choice(all_customer_ids)
            total_amount = round(random.uniform(20.0, 1000.0), 2)
            cursor.execute(
                "INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s)",
                (cid, total_amount),
            )
            orders_created += 1

            if orders_created % 500 == 0:
                print(f"  Created {orders_created} orders...")

    print(f"✓ Created {orders_created} total orders")

    # 4. Add order_items for bulk-inserted orders
    print(" Adding order items for bulk orders...")
    with db.get_cursor() as cursor:
        # Get orders that don't have order_items yet (from bulk insert)
        cursor.execute(
            """
            SELECT o.order_id
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.item_id IS NULL
            LIMIT 1500
        """
        )
        orders_without_items = [row[0] for row in cursor.fetchall()]

        items_added = 0
        for order_id in orders_without_items:
            num_items = random.randint(1, 4)
            selected_pids = random.sample(product_ids, num_items)

            for pid in selected_pids:
                quantity = random.randint(1, 3)
                cursor.execute(
                    "SELECT price FROM products WHERE product_id = %s", (pid,)
                )
                price_result = cursor.fetchone()
                if price_result:
                    unit_price = price_result[0]

                    cursor.execute(
                        """
                        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                        VALUES (%s, %s, %s, %s)
                    """,
                        (order_id, pid, quantity, unit_price),
                    )
                    items_added += 1

        print(f"✓ Added {items_added} order items")

    # 5. Update PostgreSQL statistics for query planner optimization
    with db.get_cursor() as cursor:
        cursor.execute("ANALYZE orders;")
        cursor.execute("ANALYZE products;")
        cursor.execute("ANALYZE order_items;")
        print("✓ Updated database statistics for query optimization")

    print("Data Seeding Completed.")
    print(
        f"\nDataset size: {len(customer_ids)} customers, {len(product_ids)} products, {orders_created} orders"
    )
    print("Dataset is now ready for analytics and index performance demonstration.")


if __name__ == "__main__":
    """
    Main entry point for standalone execution of the seeding script.

    This allows the seeding module to be run independently for:
    - Testing database setup
    - Re-seeding data during development
    - Demonstrating the seeding process

    Usage:
        python -m e_commerce_analytics_data_pipeline.databases.seed_data
    """
    try:
        init_db()
        seed_data()
    except FileNotFoundError as e:
        print(f"Schema file not found: {e}")
        print("Please ensure schema.sql exists in the sql/ directory")
    except Exception as e:
        print(f"Seeding failed: {e}")
        traceback.print_exc()

"""
E-Commerce Core Operations Module

This module provides all CRUD operations for the e-commerce system,
including transactional order creation with ACID properties.
"""

import json
from typing import Any, Dict, List

from e_commerce_analytics_data_pipeline.database.db import db
from e_commerce_analytics_data_pipeline.database.nosql import NoSQLManager
from e_commerce_analytics_data_pipeline.models import Customer, Product


class EcommerceOperations:
    """Core operations for e-commerce business logic."""

    @staticmethod
    def add_customer(customer: Customer) -> int:
        """
        Add a new customer to the database.

        Args:
            customer: Customer object containing name and email

        Returns:
            int: The newly created customer_id

        """
        query = (
            "INSERT INTO customers (name, email) VALUES (%s, %s) RETURNING customer_id;"
        )
        with db.get_cursor() as cursor:
            cursor.execute(query, (customer.name, customer.email))
            customer_id = cursor.fetchone()[0]
            return customer_id

    @staticmethod
    def add_product(product: Product) -> int:
        """
        Add a new product to the inventory with JSON metadata.

        Args:
            product: Product object with name, category, price, stock, and metadata

        Returns:
            int: The newly created product_id

        Note:
            Automatically invalidates related caches in Redis.
        """
        query = """
            INSERT INTO products (name, category, price, stock_quantity, metadata)
            VALUES (%s, %s, %s, %s, %s) RETURNING product_id;
        """
        with db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    product.name,
                    product.category,
                    product.price,
                    product.stock_quantity,
                    json.dumps(product.metadata),
                ),
            )
            product_id = cursor.fetchone()[0]

            # Invalidate product-related caches
            NoSQLManager.invalidate_cache("top_products")

            return product_id

    @staticmethod
    def create_order(customer_id: int, items: List[Dict[str, int]]) -> int:
        """
        Create a new order transactionally with ACID properties.

        This method ensures:
        1. Stock availability is checked
        2. Product rows are locked to prevent race conditions
        3. Stock is updated atomically
        4. Order and order items are created together
        5. Caches are invalidated for fresh data

        Args:
            customer_id: ID of the customer placing the order
            items: List of dictionaries with 'product_id' and 'quantity'

        Returns:
            int: The newly created order_id

        Raises:
            ValueError: If product not found or insufficient stock
        """
        with db.get_cursor() as cursor:
            total_amount = 0.0
            order_items_data = []

            for item in items:
                p_id = item["product_id"]
                qty = item["quantity"]

                # Check stock and get price (FOR UPDATE to lock the row)
                cursor.execute(
                    """
                    SELECT price, stock_quantity, name
                    FROM products
                    WHERE product_id = %s
                    FOR UPDATE
                """,
                    (p_id,),
                )
                res = cursor.fetchone()
                if not res:
                    raise ValueError(f"Product {p_id} not found")

                price, stock, product_name = res
                if stock < qty:
                    raise ValueError(
                        f"Insufficient stock for product {p_id} "
                        f"({product_name}): {qty} requested, {stock} available"
                    )

                total_amount += float(price) * qty
                order_items_data.append(
                    {
                        "product_id": p_id,
                        "quantity": qty,
                        "price": float(price),
                        "product_name": product_name,
                    }
                )

                # Update stock
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                    (qty, p_id),
                )

            # Create Order
            cursor.execute(
                "INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s) RETURNING order_id",
                (customer_id, total_amount),
            )
            order_id = cursor.fetchone()[0]

            # Create Order Items
            for item_data in order_items_data:
                cursor.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                """,
                    (
                        order_id,
                        item_data["product_id"],
                        item_data["quantity"],
                        item_data["price"],
                    ),
                )

            NoSQLManager.invalidate_cache()

            return order_id

    @staticmethod
    def get_customer_orders(customer_id: int) -> List[Any]:
        """
        Retrieve all orders for a specific customer with aggregated information.

        Args:
            customer_id: ID of the customer

        Returns:
            List of tuples containing order details including:
            - order_id, order_date, total_amount, item_count, product_names
        """
        query = """
            SELECT
                o.order_id,
                o.order_date,
                o.total_amount,
                COUNT(oi.item_id) as item_count,
                STRING_AGG(p.name, ', ') as products
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.customer_id = %s
            GROUP BY o.order_id
            ORDER BY o.order_date DESC
            LIMIT 10
        """
        with db.get_cursor() as cursor:
            cursor.execute(query, (customer_id,))
            return cursor.fetchall()

    @staticmethod
    def update_product_stock(product_id: int, quantity_change: int) -> bool:
        """
        Update product stock quantity with safety check.

        Args:
            product_id: ID of the product to update
            quantity_change: Positive to add stock, negative to remove stock

        Returns:
            bool: True if update was successful, False if would result in negative stock

        Note:
            Automatically invalidates related caches in Redis.
        """
        query = """
            UPDATE products
            SET stock_quantity = stock_quantity + %s
            WHERE product_id = %s AND stock_quantity + %s >= 0
            RETURNING product_id;
        """
        with db.get_cursor() as cursor:
            cursor.execute(query, (quantity_change, product_id, quantity_change))
            result = cursor.fetchone()

            if result:
                NoSQLManager.invalidate_cache("top_products")
                return True
            return False

    @staticmethod
    def get_product_metadata_by_attribute(attribute: str, value: Any):
        """
        Query products by JSONB metadata attribute using containment operator.

        Args:
            attribute: JSON key to search for
            value: Value to match for the given attribute

        Returns:
            List of product records matching the criteria

        Example:
            >>> products = EcommerceOperations.get_product_metadata_by_attribute("rating", 5)
        """
        query = """
            SELECT product_id, name, category, price, metadata
            FROM products
            WHERE metadata @> %s::jsonb
            LIMIT 10
        """
        json_filter = json.dumps({attribute: value})

        with db.get_cursor() as cursor:
            cursor.execute(query, (json_filter,))
            return cursor.fetchall()

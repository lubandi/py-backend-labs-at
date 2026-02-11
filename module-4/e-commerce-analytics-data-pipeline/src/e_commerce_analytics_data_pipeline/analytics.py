"""
Analytics Engine for E-Commerce Data Pipeline

Contains complex SQL queries for business analytics including:
- Window functions for rankings
- Common Table Expressions for aggregations
- Query performance analysis tools
"""

import re

from e_commerce_analytics_data_pipeline.database.postgres import db


class AnalyticsEngine:
    """Main analytics engine for processing e-commerce data."""

    @staticmethod
    def get_top_products_by_category():
        """
        Rank products by sales volume within each category using Window Function.

        Returns:
            List of tuples: (category, product_name, total_sold, rank)
        """
        query = """
        WITH product_sales AS (
            SELECT
                p.category,
                p.name,
                SUM(oi.quantity) as total_sold
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.category, p.product_id
        )
        SELECT
            category,
            name,
            total_sold,
            RANK() OVER (PARTITION BY category ORDER BY total_sold DESC) as rank
        FROM product_sales
        ORDER BY category, rank
        """
        with db.get_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_customer_ltv():
        """
        Calculate total revenue per customer using Common Table Expression.

        Returns:
            List of tuples: (customer_name, email, lifetime_value)
        """
        query = """
        WITH customer_revenue AS (
            SELECT
                customer_id,
                SUM(total_amount) as lifetime_value
            FROM orders
            GROUP BY customer_id
        )
        SELECT
            c.name,
            c.email,
            cr.lifetime_value
        FROM customers c
        JOIN customer_revenue cr ON c.customer_id = cr.customer_id
        ORDER BY cr.lifetime_value DESC
        """
        with db.get_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def analyze_query_performance(query: str):
        """
        Run EXPLAIN ANALYZE on a query and return the execution plan.

        Args:
            query: SQL query to analyze

        Returns:
            List of tuples containing the query plan
        """
        explain_query = f"EXPLAIN ANALYZE {query}"
        with db.get_cursor() as cursor:
            cursor.execute(explain_query)
            return cursor.fetchall()

    @staticmethod
    def extract_execution_time(plan_rows):
        """
        Extract execution time from EXPLAIN ANALYZE output.

        Args:
            plan_rows: Query plan rows from EXPLAIN ANALYZE

        Returns:
            float: Execution time in milliseconds, or None if not found
        """
        if not plan_rows:
            return None

        # Look for actual time in the plan
        for row in plan_rows:
            plan_text = row[0]
            # Match pattern: actual time=0.123..0.456
            match = re.search(r"actual time=([\d\.]+)\.\.([\d\.]+)", plan_text)
            if match:
                return float(match.group(2)) * 1000  # Convert to milliseconds

        return None

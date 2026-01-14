"""
Data Models for E-Commerce System

This module defines the data classes used throughout the application.
These models represent the core business entities in the e-commerce domain.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Customer:
    """
    Customer entity representing an e-commerce customer.

    Attributes:
        name: Full name of the customer
        email: Email address (must be unique)
        customer_id: Auto-generated primary key (optional for new customers)
        created_at: Timestamp of account creation (auto-generated)
    """

    name: str
    email: str
    customer_id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Product:
    """
    Product entity representing items available for purchase.

    Attributes:
        name: Product name
        category: Product category (e.g., Electronics, Books)
        price: Unit price in decimal
        stock_quantity: Available quantity in inventory
        metadata: Flexible JSONB attributes (color, rating, material, etc.)
        product_id: Auto-generated primary key (optional for new products)
    """

    name: str
    category: str
    price: float
    stock_quantity: int
    metadata: Dict[str, Any]
    product_id: Optional[int] = None


@dataclass
class OrderItem:
    """
    Order item entity representing a line item in an order.

    Attributes:
        product_id: Reference to the product
        quantity: Number of units ordered
        unit_price: Price per unit at time of order
        item_id: Auto-generated primary key (optional for new items)
    """

    product_id: int
    quantity: int
    unit_price: float
    item_id: Optional[int] = None


@dataclass
class Order:
    """
    Order entity representing a customer purchase.

    Attributes:
        customer_id: Reference to the customer
        items: List of OrderItem objects
        total_amount: Total order amount
        order_id: Auto-generated primary key (optional for new orders)
        order_date: Timestamp of order creation (auto-generated)
    """

    customer_id: int
    items: List[OrderItem]
    total_amount: float
    order_id: Optional[int] = None
    order_date: Optional[datetime] = None

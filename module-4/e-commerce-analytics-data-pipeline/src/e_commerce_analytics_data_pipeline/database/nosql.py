"""
NoSQL Integration Module for Redis and MongoDB

This module provides:
- Redis caching for frequently accessed data
- MongoDB session storage for shopping carts
- Connection management with health checks
"""

import json
import os
from datetime import datetime, timedelta

import redis
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Global connection flags and objects
redis_connected = False
mongo_connected = False
redis_client = None
mongo_client = None
cart_collection = None

# Redis Connection
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True,
        socket_connect_timeout=3,
    )
    # Test connection
    redis_client.ping()
    redis_connected = True
    print("✓ Redis connected successfully")
except Exception as e:
    print(f"✗ Redis connection failed: {e}")
    redis_client = None
    redis_connected = False

# MongoDB Connection
try:
    mongo_client = MongoClient(
        host=os.getenv("MONGO_HOST", "localhost"),
        port=int(os.getenv("MONGO_PORT", 27017)),
        serverSelectionTimeoutMS=3000,
    )
    # Test connection
    mongo_client.admin.command("ping")
    mongo_db = mongo_client["shop_session"]
    cart_collection = mongo_db["carts"]
    mongo_connected = True
    print("✓ MongoDB connected successfully")
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")
    mongo_client = None
    mongo_connected = False
    cart_collection = None


class NoSQLManager:
    """Manager class for NoSQL database operations."""

    @staticmethod
    def cache_top_products(products: list, ttl: int = 3600) -> bool:
        """
        Cache top products in Redis with Time-To-Live.

        Args:
            products: List of products or customer data to cache
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            bool: True if caching successful, False otherwise
        """
        if not redis_connected or redis_client is None:
            print("⚠️ Redis not available, skipping cache")
            return False

        try:
            # Cache for specified time (default 1 hour)
            redis_client.setex("top_products", ttl, json.dumps(products, default=str))
            print(f"✓ Cached {len(products)} products in Redis (TTL: {ttl}s)")
            return True
        except Exception as e:
            print(f"✗ Redis Cache Error: {e}")
            return False

    @staticmethod
    def get_cached_top_products():
        """
        Retrieve cached top products from Redis.

        Returns:
            list: Cached data or None if not found/error
        """
        if not redis_connected or redis_client is None:
            return None

        try:
            data = redis_client.get("top_products")
            if data:
                print("✓ Retrieved from Redis cache")
                return json.loads(data)
            else:
                print("⚠️ No data in Redis cache")
                return None
        except Exception as e:
            print(f"✗ Redis Read Error: {e}")
            return None

    @staticmethod
    def invalidate_cache(key: str = None):
        """
        Invalidate cache entries in Redis.
        If no key specified, invalidates all relevant caches.
        """
        if not redis_connected or redis_client is None:
            return

        try:
            if key:
                redis_client.delete(key)
            else:
                cache_keys = ["top_products"]
                for cache_key in cache_keys:
                    if redis_client.exists(cache_key):
                        redis_client.delete(cache_key)
        except Exception as e:
            print(f"✗ Cache Invalidation Error: {e}")

    @staticmethod
    def save_cart_session(
        session_id: str, cart_items: list, ttl_hours: int = 24
    ) -> bool:
        """
        Save shopping cart session to MongoDB with expiration.

        Args:
            session_id: Unique identifier for the user session
            cart_items: List of cart items with product details
            ttl_hours: Time to live in hours (default: 24 hours)

        Returns:
            bool: True if save successful, False otherwise
        """
        if not mongo_connected or cart_collection is None:
            print("⚠️ MongoDB not available, skipping cart save")
            return False

        try:
            cart_document = {
                "session_id": session_id,
                "items": cart_items,
                "created_at": NoSQLManager._get_current_timestamp(),
                "expires_at": NoSQLManager._get_future_timestamp(ttl_hours),
            }

            result = cart_collection.update_one(
                {"session_id": session_id}, {"$set": cart_document}, upsert=True
            )

            if result.upserted_id:
                print(f"✓ Created new cart session: {session_id}")
            else:
                print(f"✓ Updated existing cart session: {session_id}")

            return True
        except Exception as e:
            print(f"✗ MongoDB Write Error: {e}")
            return False

    @staticmethod
    def get_cart_session(session_id: str):
        """
        Retrieve shopping cart session from MongoDB.

        Args:
            session_id: Unique identifier for the user session

        Returns:
            list: Cart items or empty list if not found
        """
        if not mongo_connected or cart_collection is None:
            print("⚠️ MongoDB not available")
            return []

        try:
            doc = cart_collection.find_one(
                {"session_id": session_id}, {"_id": 0, "items": 1}
            )

            if doc and "items" in doc:
                print(f"✓ Retrieved cart session: {session_id}")
                return doc["items"]
            else:
                print(f"⚠️ No cart found for session: {session_id}")
                return []
        except Exception as e:
            print(f"✗ MongoDB Read Error: {e}")
            return []

    @staticmethod
    def clear_cart_session(session_id: str) -> bool:
        """
        Clear shopping cart session from MongoDB.

        Args:
            session_id: Unique identifier for the user session

        Returns:
            bool: True if deletion successful, False otherwise
        """
        if not mongo_connected or cart_collection is None:
            return False

        try:
            result = cart_collection.delete_one({"session_id": session_id})
            if result.deleted_count > 0:
                print(f"✓ Cleared cart session: {session_id}")
                return True
            else:
                print(f"⚠️ No cart to clear for session: {session_id}")
                return False
        except Exception as e:
            print(f"✗ MongoDB Delete Error: {e}")
            return False

    @staticmethod
    def _get_current_timestamp():
        """
        Helper to get current UTC timestamp.

        Returns:
            datetime: Current UTC datetime
        """
        return datetime.now()

    @staticmethod
    def _get_future_timestamp(hours: int):
        """
        Helper to get future timestamp for TTL.

        Args:
            hours: Number of hours in the future

        Returns:
            datetime: Future UTC datetime
        """
        return datetime.now() + timedelta(hours=hours)

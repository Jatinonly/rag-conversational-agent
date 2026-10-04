import hashlib

from redis.exceptions import RedisError

from logging_config import logger
from redis_client import redis_client


def make_cache_key(
    conversation_id: str,
    question: str,
    document_id: str | None,
) -> str:
    raw = f"{conversation_id}:{question.strip().lower()}:{document_id}"
    return "answer:" + hashlib.sha256(raw.encode()).hexdigest()


def cache_get(key: str) -> str | None:
    try:
        return redis_client.get(key)
    except RedisError:
        logger.warning("Redis unavailable, skipping cache read")
        return None


def cache_set(key: str, value: str, ttl: int = 3600) -> None:
    try:
        redis_client.setex(key, ttl, value)
    except RedisError:
        logger.warning("Redis unavailable, skipping cache write")


def clear_answer_cache() -> None:
    try:
        for key in redis_client.scan_iter("answer:*"):
            redis_client.delete(key)
    except RedisError:
        logger.warning("Redis unavailable, could not clear cache")

import asyncio
import uuid
import time
import logging

from ..models.msg import Msg, Update, Status, CipherText, Key
from .redis import redis_client as r

from ..redis_db.msg import (
    store_message,
    get_message,
    update_message_status,
    get_status,
    get_routing,
    get_messages_since,
    get_updates_since,
    null_message
)

log = logging.getLogger("uvicorn.error")


async def run_redis_tests():
    log.info("========== STARTING REDIS TEST SUITE ==========")

    # --- Setup unique IDs ---
    test_id = f"test:{uuid.uuid4()}"
    sender = f"user:{uuid.uuid4()}"
    recipient = f"user:{uuid.uuid4()}"
    now = time.time()

    try:
        # --- Create test message ---
        msg = Msg(
            msg_id=test_id,
            sender_uid=sender,
            recipient_uid=recipient,
            ciphertext=CipherText(
                ciphertext="hello",
                IV="iv123",
                tag="tag123"
            ),
            key=Key(
                algorithm="aes",
                encrypted_key="key123"
            ),
            status=Status.SENT,
            timestamp=int(now),
            ttl=0
        )

        # --- STORE ---
        res = await store_message(msg)
        assert res is not None
        log.info("PASS: store_message")

        # --- GET ---
        fetched = await get_message(test_id)
        assert fetched.msg_id == test_id
        assert fetched.sender_uid == sender
        assert fetched.recipient_uid == recipient
        log.info("PASS: get_message")

        # --- ROUTING ---
        routing = await get_routing(test_id)
        assert routing[0] == sender
        assert routing[1] == recipient
        log.info("PASS: get_routing")

        # --- STATUS ---
        status = await get_status(test_id)
        assert status.status == Status.SENT
        log.info("PASS: get_status")

        # --- UPDATE STATUS ---
        update = Update(msg_id=test_id, status=Status.DELIVERED)
        await update_message_status(update)

        updated_status = await get_status(test_id)
        assert updated_status.status == Status.DELIVERED
        log.info("PASS: update_message_status")

        # --- GET MESSAGES SINCE ---
        msgs = await get_messages_since(sender, now - 10)
        assert any(test_id in m for m in msgs)
        log.info("PASS: get_messages_since")

        # --- GET UPDATES SINCE ---
        updates = await get_updates_since(sender, now - 10)
        assert any(test_id in u for u in updates)
        log.info("PASS: get_updates_since")

        # --- NULL MESSAGE ---
        await null_message(test_id)

        nulled = await get_message(test_id)
        assert nulled.status == Status.DELETED
        assert nulled.recipient_uid == ""
        log.info("PASS: null_message")

    except AssertionError as e:
        log.error("[FAIL] TEST FAILED: %s", str(e))
        raise

    except Exception as e:
        log.error("[FAIL] UNEXPECTED ERROR: %s", str(e))
        raise

    finally:
        # --- CLEANUP ---
        log.info("Cleaning up test data...")

        await r.delete(f"msg:{test_id}")
        await r.zrem(f"user_msgs:{sender}", test_id)
        await r.zrem(f"user_msgs:{recipient}", test_id)
        await r.zrem(f"user_updates:{sender}", test_id)
        await r.zrem(f"user_updates:{recipient}", test_id)

        log.info("========== REDIS TEST SUITE COMPLETE ==========")
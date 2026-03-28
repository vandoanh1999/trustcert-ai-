
import sys
from unittest.mock import MagicMock

# Mock heavy modules
mock_torch = MagicMock()
mock_torch.nn = MagicMock()
mock_torch.optim = MagicMock()
sys.modules["torch"] = mock_torch
sys.modules["torch.nn"] = mock_torch.nn
sys.modules["torch.optim"] = mock_torch.optim

sys.modules["faiss"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["llama_cpp"] = MagicMock()

import numpy as np
import time
import asyncio
import logging
from pathlib import Path

# Ensure we can import from the root
sys.path.insert(0, str(Path(__file__).parent))

# Import components (some will be mocked)
from core.fvs_storage import FaissVectorStore
from core.p2p_gossip import GossipP2P
from core.secure_dtq import MPCDistributedTaskQueue
from core.consensus import ProofOfContribution
from core.anchor_sync_v2 import DecentralizedSnapshot
from services.user_profile.profile_router import ProfileBasedRouter, UserTier
from aurora_trust.reputation_vc import get_reputation, update_reputation_with_feedback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_reputation_caching():
    logger.info("🧪 Testing Reputation Caching...")
    expert_id = "test_expert_regression"

    # Initial update
    score1 = update_reputation_with_feedback(expert_id, 0.8)
    logger.info(f"   Initial score: {score1}")

    # Get from cache/file
    score2 = get_reputation(expert_id)
    logger.info(f"   Fetched score: {score2}")

    assert score1 == score2, f"Scores don't match: {score1} != {score2}"

    # Update again
    score3 = update_reputation_with_feedback(expert_id, 0.9)
    logger.info(f"   Updated score: {score3}")

    # Get again
    score4 = get_reputation(expert_id)
    logger.info(f"   Final fetched score: {score4}")

    assert score3 == score4, f"Final scores don't match: {score3} != {score4}"
    logger.info("✅ Reputation caching test passed!")

async def main():
    try:
        await test_reputation_caching()
        logger.info("\n✅ ALL REGRESSION TESTS PASSED!")
    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

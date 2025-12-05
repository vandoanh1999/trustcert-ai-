"""
Genesis Core V8: User Management and Tier Progression (Refactored)

This version uses the centralized config for all parameters.
"""
from enum import Enum
from aurora_trust.reputation_vc import issue_tier_credential
from core.config import *

class UserTier(Enum):
    EPHEMERAL = 1
    STABLE = 2
    VIP_PRO = 3

class User:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.tier = UserTier.EPHEMERAL
        self.contribution_score = 0.0
        self.credentials = []

    def add_contribution(self, score: float, is_high_quality_feedback: bool = False):
        base_score = score
        if is_high_quality_feedback:
            base_score += USER_HIGH_QUALITY_FEEDBACK_BONUS
            print(f"[User {self.user_id}] Received +{USER_HIGH_QUALITY_FEEDBACK_BONUS} contribution bonus!")
        self.contribution_score += base_score
        self.update_tier()

    def update_tier(self):
        current_tier = self.tier
        if self.contribution_score >= USER_VIP_PRO_CONTRIBUTION_THRESHOLD and self.tier != UserTier.VIP_PRO:
            self.tier = UserTier.VIP_PRO
            vc = issue_tier_credential(self.user_id, self.tier.name, self.contribution_score)
            self.credentials.append(vc)
        elif self.contribution_score >= USER_STABLE_CONTRIBUTION_THRESHOLD and self.tier == UserTier.EPHEMERAL:
            self.tier = UserTier.STABLE
            vc = issue_tier_credential(self.user_id, self.tier.name, self.contribution_score)
            self.credentials.append(vc)
        if self.tier != current_tier:
            print(f"[User {self.user_id}] Tier updated: {current_tier.name} -> {self.tier.name}")

    def get_status(self) -> dict:
        return {
            "user_id": self.user_id, "tier": self.tier.name,
            "contribution_score": round(self.contribution_score, 4),
            "credentials_issued": len(self.credentials)
        }

"""Tenant-isolated dual-entry ledger repository."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import func, select
from app.domain.ledger_plan import GoldJournalEntry, MoneyJournalEntry
from app.models.entities import (
    GoldJournalEntryModel,
    GoldJournalLineModel,
    MoneyJournalEntryModel,
    MoneyJournalLineModel,
)
from app.repos.base import BaseTenantRepository

class LedgerRepository(BaseTenantRepository):
    def post_gold_entry(
        self,
        entry: GoldJournalEntry,
        exchange_id: uuid.UUID | None = None,
        receipt_hash: str | None = None,
    ) -> GoldJournalEntryModel:
        # Pre-verify balance in Python domain before hitting DB triggers
        entry.assert_balanced()

        entry_model = GoldJournalEntryModel(
            id=uuid.uuid4(),
            shop_id=self.shop_id,
            exchange_id=exchange_id,
            receipt_hash=receipt_hash,
            entry_name=entry.entry_name,
            description=entry.description,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(entry_model)

        for line in entry.lines:
            line_model = GoldJournalLineModel(
                id=uuid.uuid4(),
                entry_id=entry_model.id,
                shop_id=self.shop_id,
                account=line.account,
                side=line.side,
                amount_ug=int(line.amount_ug),
            )
            self.session.add(line_model)

        self.session.flush()
        return entry_model

    def post_money_entry(
        self,
        entry: MoneyJournalEntry,
        exchange_id: uuid.UUID | None = None,
        receipt_hash: str | None = None,
    ) -> MoneyJournalEntryModel:
        # Pre-verify balance in Python domain before hitting DB triggers
        entry.assert_balanced()

        entry_model = MoneyJournalEntryModel(
            id=uuid.uuid4(),
            shop_id=self.shop_id,
            exchange_id=exchange_id,
            receipt_hash=receipt_hash,
            entry_name=entry.entry_name,
            description=entry.description,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(entry_model)

        for line in entry.lines:
            line_model = MoneyJournalLineModel(
                id=uuid.uuid4(),
                entry_id=entry_model.id,
                shop_id=self.shop_id,
                account=line.account,
                side=line.side,
                amount_paise=int(line.amount_paise),
            )
            self.session.add(line_model)

        self.session.flush()
        return entry_model

    def get_gold_account_balance(self, account: str) -> int:
        """Derive dynamic account balance in micrograms (Debits - Credits)."""
        stmt = (
            select(
                func.coalesce(
                    func.sum(
                        func.case(
                            (GoldJournalLineModel.side == "D", GoldJournalLineModel.amount_ug),
                            else_=-GoldJournalLineModel.amount_ug,
                        )
                    ),
                    0,
                )
            )
            .where(
                GoldJournalLineModel.shop_id == self.shop_id,
                GoldJournalLineModel.account == account,
            )
        )
        return int(self.session.execute(stmt).scalar_one())

    def get_money_account_balance(self, account: str) -> int:
        """Derive dynamic account balance in paise (Debits - Credits)."""
        stmt = (
            select(
                func.coalesce(
                    func.sum(
                        func.case(
                            (MoneyJournalLineModel.side == "D", MoneyJournalLineModel.amount_paise),
                            else_=-MoneyJournalLineModel.amount_paise,
                        )
                    ),
                    0,
                )
            )
            .where(
                MoneyJournalLineModel.shop_id == self.shop_id,
                MoneyJournalLineModel.account == account,
            )
        )
        return int(self.session.execute(stmt).scalar_one())

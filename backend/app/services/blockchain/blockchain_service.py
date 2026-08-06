import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Address, AddressType, Block, Chain, Transaction, TxStatus, TxType
from app.schemas.blockchain import ChainCreate, ChainUpdate


def create_chain(session: Session, chain_in: ChainCreate) -> Chain:
    db_chain = Chain(**chain_in.model_dump())
    session.add(db_chain)
    session.commit()
    session.refresh(db_chain)
    return db_chain


def get_chain(session: Session, chain_id: uuid.UUID) -> Optional[Chain]:
    return session.get(Chain, chain_id)


def list_chains(session: Session, active_only: bool = False, skip: int = 0, limit: int = 100) -> List[Chain]:
    stmt = select(Chain)
    if active_only:
        stmt = stmt.where(Chain.is_active.is_(True))
    return list(session.execute(stmt.offset(skip).limit(limit)).scalars().all())


def update_chain(session: Session, db_chain: Chain, chain_in: ChainUpdate) -> Chain:
    for field, value in chain_in.model_dump(exclude_unset=True).items():
        setattr(db_chain, field, value)
    session.add(db_chain)
    session.commit()
    session.refresh(db_chain)
    return db_chain


def get_block_by_number(session: Session, chain_id: uuid.UUID, block_number: int) -> Optional[Block]:
    return session.execute(
        select(Block).where(Block.chain_id == chain_id, Block.block_number == block_number)
    ).scalar_one_or_none()


def get_latest_synced_block_number(session: Session, chain_id: uuid.UUID) -> Optional[int]:
    row = session.execute(
        select(Block.block_number).where(Block.chain_id == chain_id).order_by(Block.block_number.desc()).limit(1)
    ).scalar_one_or_none()
    return row


def list_blocks(session: Session, chain_id: uuid.UUID, skip: int = 0, limit: int = 50) -> List[Block]:
    stmt = (
        select(Block)
        .where(Block.chain_id == chain_id)
        .order_by(Block.block_number.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(session.execute(stmt).scalars().all())


def upsert_block(
    session: Session,
    chain_id: uuid.UUID,
    block_number: int,
    block_hash: str,
    parent_hash: Optional[str],
    tx_count: int,
    block_timestamp: datetime,
) -> Block:
    existing = get_block_by_number(session, chain_id, block_number)
    if existing:
        existing.block_hash = block_hash
        existing.parent_hash = parent_hash
        existing.tx_count = tx_count
        existing.block_timestamp = block_timestamp
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    db_block = Block(
        chain_id=chain_id,
        block_number=block_number,
        block_hash=block_hash,
        parent_hash=parent_hash,
        tx_count=tx_count,
        block_timestamp=block_timestamp,
    )
    session.add(db_block)
    session.commit()
    session.refresh(db_block)
    return db_block


def get_transaction_by_hash(session: Session, chain_id: uuid.UUID, tx_hash: str) -> Optional[Transaction]:
    return session.execute(
        select(Transaction).where(Transaction.chain_id == chain_id, Transaction.tx_hash == tx_hash)
    ).scalar_one_or_none()


def list_transactions_for_address(
    session: Session, chain_id: uuid.UUID, address: str, skip: int = 0, limit: int = 50
) -> List[Transaction]:
    stmt = (
        select(Transaction)
        .where(
            Transaction.chain_id == chain_id,
            (Transaction.from_address == address) | (Transaction.to_address == address),
        )
        .order_by(Transaction.block_number.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(session.execute(stmt).scalars().all())


def upsert_transaction(
    session: Session,
    chain_id: uuid.UUID,
    tx_hash: str,
    block_number: Optional[int],
    from_address: str,
    to_address: Optional[str],
    value: int,
    gas_used: Optional[int],
    gas_price: Optional[int],
    status: TxStatus,
    tx_type: Optional[TxType] = None,
) -> Transaction:
    existing = get_transaction_by_hash(session, chain_id, tx_hash)
    if existing:
        existing.block_number = block_number
        existing.status = status
        existing.gas_used = gas_used
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    db_tx = Transaction(
        chain_id=chain_id,
        tx_hash=tx_hash,
        block_number=block_number,
        from_address=from_address,
        to_address=to_address,
        value=value,
        gas_used=gas_used,
        gas_price=gas_price,
        status=status,
        tx_type=tx_type,
    )
    session.add(db_tx)
    session.commit()
    session.refresh(db_tx)
    return db_tx



def get_or_create_address(session: Session, chain_id: uuid.UUID, address: str) -> Address:
    existing = session.execute(
        select(Address).where(Address.chain_id == chain_id, Address.address == address)
    ).scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if existing:
        existing.last_seen_at = now
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    db_addr = Address(
        chain_id=chain_id,
        address=address,
        address_type=AddressType.unknown,
        first_seen_at=now,
        last_seen_at=now,
    )
    session.add(db_addr)
    session.commit()
    session.refresh(db_addr)
    return db_addr


def get_address(session: Session, chain_id: uuid.UUID, address: str) -> Optional[Address]:
    return session.execute(
        select(Address).where(Address.chain_id == chain_id, Address.address == address)
    ).scalar_one_or_none()


def update_address_label(session: Session, db_address: Address, label: str) -> Address:
    db_address.label = label
    session.add(db_address)
    session.commit()
    session.refresh(db_address)
    return db_address


MAX_BLOCKS_PER_SYNC = 10  # keep this low; public/free RPC endpoints rate-limit aggressively


def sync_latest_evm_blocks(session: Session, chain: Chain, max_blocks: int = MAX_BLOCKS_PER_SYNC) -> dict:
    """
    Pulls the most recent `max_blocks` blocks (and their transactions) from the
    chain's RPC endpoint and upserts them. Deliberately synchronous and capped —
    this is meant to be called from an endpoint or a cron hitting it every
    minute or so, not a firehose indexer. Swap for a proper async worker queue
    once you're past the free tier.
    """
    try:
        from web3 import Web3
    except ImportError:
        raise RuntimeError("web3.py is required for EVM sync — pip install web3")

    if not chain.rpc_url:
        raise ValueError("Chain has no rpc_url configured")

    w3 = Web3(Web3.HTTPProvider(chain.rpc_url))
    latest = w3.eth.block_number
    already_synced = get_latest_synced_block_number(session, chain.id)
    start = (already_synced + 1) if already_synced is not None else max(latest - max_blocks + 1, 0)
    end = min(latest, start + max_blocks - 1)

    blocks_synced = 0
    txs_synced = 0

    for block_number in range(start, end + 1):
        block = w3.eth.get_block(block_number, full_transactions=True)
        block_ts = datetime.fromtimestamp(block["timestamp"], tz=timezone.utc)

        upsert_block(
            session,
            chain_id=chain.id,
            block_number=block["number"],
            block_hash=block["hash"].hex(),
            parent_hash=block["parentHash"].hex(),
            tx_count=len(block["transactions"]),
            block_timestamp=block_ts,
        )
        blocks_synced += 1

        for tx in block["transactions"]:
            try:
                receipt = w3.eth.get_transaction_receipt(tx["hash"])
                status = TxStatus.success if receipt["status"] == 1 else TxStatus.failed
                gas_used = receipt["gasUsed"]
            except Exception:
                status = TxStatus.pending
                gas_used = None

            to_addr = tx["to"]
            upsert_transaction(
                session,
                chain_id=chain.id,
                tx_hash=tx["hash"].hex(),
                block_number=block["number"],
                from_address=tx["from"],
                to_address=to_addr,
                value=int(tx["value"]),
                gas_used=gas_used,
                gas_price=int(tx.get("gasPrice") or 0),
                status=status,
                tx_type=TxType.contract_creation if to_addr is None else TxType.transfer,
            )
            get_or_create_address(session, chain.id, tx["from"])
            if to_addr:
                get_or_create_address(session, chain.id, to_addr)
            txs_synced += 1

    return {
        "chain_id": chain.id,
        "blocks_synced": blocks_synced,
        "transactions_synced": txs_synced,
        "from_block": start,
        "to_block": end,
    }

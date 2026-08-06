import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.blockchain.blockchain import AddressType, ChainType, TxStatus, TxType


class ChainCreate(BaseModel):
    name: str
    chain_type: ChainType
    chain_id_numeric: Optional[int] = None
    rpc_url: Optional[str] = None
    explorer_url: Optional[str] = None
    native_symbol: Optional[str] = None
    is_testnet: bool = False


class ChainUpdate(BaseModel):
    name: Optional[str] = None
    rpc_url: Optional[str] = None
    explorer_url: Optional[str] = None
    is_active: Optional[bool] = None


class ChainRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    chain_type: ChainType
    chain_id_numeric: Optional[int]
    rpc_url: Optional[str]
    explorer_url: Optional[str]
    native_symbol: Optional[str]
    is_testnet: bool
    is_active: bool
    created_at: datetime



class BlockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    chain_id: uuid.UUID
    block_number: int
    block_hash: str
    parent_hash: Optional[str]
    tx_count: int
    block_timestamp: datetime



class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    chain_id: uuid.UUID
    tx_hash: str
    block_number: Optional[int]
    from_address: str
    to_address: Optional[str]
    value: int
    gas_used: Optional[int]
    gas_price: Optional[int]
    status: TxStatus
    tx_type: Optional[TxType]



class AddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    chain_id: uuid.UUID
    address: str
    address_type: AddressType
    label: Optional[str]
    first_seen_at: Optional[datetime]
    last_seen_at: Optional[datetime]


class AddressLabelUpdate(BaseModel):
    label: str



class SyncResult(BaseModel):
    chain_id: uuid.UUID
    blocks_synced: int
    transactions_synced: int
    from_block: int
    to_block: int

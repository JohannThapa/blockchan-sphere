from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentSuperuser, CurrentUser, SessionDep, require_permission
from app.schemas.blockchain import (
    AddressLabelUpdate,
    AddressRead,
    BlockRead,
    ChainCreate,
    ChainRead,
    ChainUpdate,
    SyncResult,
    TransactionRead,
)
from app.services.blockchain.blockchain_service import (
    create_chain,
    get_address,
    get_chain,
    list_blocks,
    list_chains,
    list_transactions_for_address,
    sync_latest_evm_blocks,
    update_address_label,
    update_chain,
)

router = APIRouter(prefix="/blockchain", tags=["Blockchain Core"])


@router.post("/chains", response_model=ChainRead)
def add_chain(session: SessionDep, chain_in: ChainCreate, current_user: CurrentSuperuser):
    return create_chain(session, chain_in)


@router.get("/chains", response_model=List[ChainRead])
def get_chains(session: SessionDep, current_user: CurrentUser, active_only: bool = False):
    return list_chains(session, active_only=active_only)


@router.get("/chains/{chain_id}", response_model=ChainRead)
def get_chain_by_id(session: SessionDep, chain_id: UUID, current_user: CurrentUser):
    chain = get_chain(session, chain_id)
    if not chain:
        raise HTTPException(404, "Chain not found")
    return chain


@router.put("/chains/{chain_id}", response_model=ChainRead)
def edit_chain(session: SessionDep, chain_id: UUID, chain_in: ChainUpdate, current_user: CurrentSuperuser):
    chain = get_chain(session, chain_id)
    if not chain:
        raise HTTPException(404, "Chain not found")
    return update_chain(session, chain, chain_in)


@router.get("/chains/{chain_id}/blocks", response_model=List[BlockRead])
def explorer_blocks(session: SessionDep, chain_id: UUID, current_user: CurrentUser, skip: int = 0, limit: int = 50):
    if limit > 100:
        raise HTTPException(400, "limit must be <= 100")
    return list_blocks(session, chain_id, skip, limit)


@router.get("/chains/{chain_id}/addresses/{address}", response_model=AddressRead)
def explorer_address(session: SessionDep, chain_id: UUID, address: str, current_user: CurrentUser):
    addr = get_address(session, chain_id, address)
    if not addr:
        raise HTTPException(404, "Address not seen on this chain yet")
    return addr


@router.put("/chains/{chain_id}/addresses/{address}/label", response_model=AddressRead)
def label_address(
    session: SessionDep, chain_id: UUID, address: str, label_in: AddressLabelUpdate, current_user: CurrentUser
):
    require_permission(session, current_user, "address.label")
    addr = get_address(session, chain_id, address)
    if not addr:
        raise HTTPException(404, "Address not seen on this chain yet")
    return update_address_label(session, addr, label_in.label)


@router.get("/chains/{chain_id}/addresses/{address}/transactions", response_model=List[TransactionRead])
def explorer_address_transactions(
    session: SessionDep, chain_id: UUID, address: str, current_user: CurrentUser, skip: int = 0, limit: int = 50
):
    if limit > 100:
        raise HTTPException(400, "limit must be <= 100")
    return list_transactions_for_address(session, chain_id, address, skip, limit)


@router.post("/chains/{chain_id}/sync", response_model=SyncResult)
def trigger_sync(session: SessionDep, chain_id: UUID, current_user: CurrentUser, max_blocks: int = 10):
    require_permission(session, current_user, "chain.sync")
    chain = get_chain(session, chain_id)
    if not chain:
        raise HTTPException(404, "Chain not found")
    if not chain.is_active:
        raise HTTPException(400, "Chain is not active")
    if max_blocks > 10:
        raise HTTPException(400, "max_blocks capped at 10 per call on free tier — call again to page forward")
    try:
        return sync_latest_evm_blocks(session, chain, max_blocks=max_blocks)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Client, TimeEntry
from app.schemas import (
    UserCreate, Token, ClientCreate, ClientOut,
    TimeEntryCreate, TimeEntryOut,
)
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api")

# ── Auth ──────────────────────────────────────────────────────────────

@router.post("/auth/register", response_model=Token, status_code=201)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already taken")
    user = User(username=body.username, hashed_password=hash_password(body.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return Token(access_token=create_access_token(user.id))


@router.post("/auth/login", response_model=Token)
async def login(body: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_access_token(user.id))


# ── Clients ───────────────────────────────────────────────────────────

@router.get("/clients", response_model=list[ClientOut])
async def list_clients(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(
            Client.id, Client.name, Client.rate,
            func.coalesce(func.sum(TimeEntry.hours), 0).label("total_hours"),
        )
        .outerjoin(TimeEntry, TimeEntry.client_id == Client.id)
        .where(Client.user_id == user.id)
        .group_by(Client.id)
        .order_by(Client.name)
    )
    rows = (await db.execute(stmt)).all()
    return [
        ClientOut(id=r.id, name=r.name, rate=r.rate, total_hours=r.total_hours)
        for r in rows
    ]


@router.post("/clients", response_model=ClientOut, status_code=201)
async def create_client(
    body: ClientCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    client = Client(name=body.name, rate=body.rate, user_id=user.id)
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return ClientOut(id=client.id, name=client.name, rate=client.rate, total_hours=0)


@router.delete("/clients/{client_id}", status_code=204)
async def delete_client(
    client_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.user_id == user.id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    await db.delete(client)
    await db.commit()


# ── Time Entries ──────────────────────────────────────────────────────

@router.get("/clients/{client_id}/entries", response_model=list[TimeEntryOut])
async def list_entries(
    client_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Client not found")

    rows = await db.execute(
        select(TimeEntry)
        .where(TimeEntry.client_id == client_id)
        .order_by(TimeEntry.date.desc())
    )
    return [
        TimeEntryOut(id=e.id, client_id=e.client_id, date=e.date, hours=e.hours, note=e.note)
        for e in rows.scalars()
    ]


@router.post("/clients/{client_id}/entries", response_model=TimeEntryOut, status_code=201)
async def create_entry(
    client_id: str,
    body: TimeEntryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Client).where(Client.id == client_id, Client.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Client not found")

    entry = TimeEntry(client_id=client_id, date=body.date, hours=body.hours, note=body.note)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return TimeEntryOut(
        id=entry.id, client_id=entry.client_id,
        date=entry.date, hours=entry.hours, note=entry.note,
    )


@router.delete("/clients/{client_id}/entries/{entry_id}", status_code=204)
async def delete_entry(
    client_id: str,
    entry_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify client ownership
    client_result = await db.execute(
        select(Client).where(Client.id == client_id, Client.user_id == user.id)
    )
    if not client_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Client not found")

    result = await db.execute(
        select(TimeEntry).where(TimeEntry.id == entry_id, TimeEntry.client_id == client_id)
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    await db.delete(entry)
    await db.commit()

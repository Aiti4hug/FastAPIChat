from fastapi import HTTPException, Depends, APIRouter
from mysite.database.models import GroupPeople, ChatGroup, UserProfile, StatusChoice
from mysite.database.schema import GroupPeopleCreateSchema, GroupPeopleOutSchema
from mysite.database.db import Session
from sqlalchemy.orm import Session
from typing import List


async def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


people_router = APIRouter(prefix='/people', tags=['Group People'])


def check_add_permission(group_id: int, current_user_id: int, db: Session):
    group = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail='Группа не найдена')

    user = db.query(UserProfile).filter(UserProfile.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    if group.owner_id != current_user_id and user.user_status != StatusChoice.admin:
        raise HTTPException(status_code=403, detail='Нет права добавлять людей.')

    return group


@people_router.post('/', response_model=dict)
async def people_create(people: GroupPeopleCreateSchema,
                        current_user_id: int, db: Session = Depends(get_db)):
    check_add_permission(people.group_id, current_user_id, db)

    user = db.query(UserProfile).filter(UserProfile.id == people.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    existing = db.query(GroupPeople).filter(
        GroupPeople.group_id == people.group_id,
        GroupPeople.user_id == people.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail='Пользователь уже вступил в группу.')

    people_db = GroupPeople(**people.dict())
    db.add(people_db)
    db.commit()
    db.refresh(people_db)
    return {'message': 'Saved'}


@people_router.get('/', response_model=List[GroupPeopleOutSchema])
async def people_list(db: Session = Depends(get_db)):
    return db.query(GroupPeople).all()


@people_router.get('/{people_id}', response_model=GroupPeopleOutSchema)
async def people_detail(people_id: int, db: Session = Depends(get_db)):
    people_db = db.query(GroupPeople).filter(GroupPeople.id == people_id).first()
    if not people_db:
        raise HTTPException(status_code=404, detail='Информация не найдена.')
    return people_db


@people_router.put('/{people_id}', response_model=GroupPeopleOutSchema)
async def people_update(people_id: int, people: GroupPeopleCreateSchema,
                        current_user_id: int, db: Session = Depends(get_db)):
    people_db = db.query(GroupPeople).filter(GroupPeople.id == people_id).first()
    if not people_db:
        raise HTTPException(status_code=404, detail='Информация не найдена.')

    check_add_permission(people.group_id, current_user_id, db)

    group = db.query(ChatGroup).filter(ChatGroup.id == people.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail='Группа не найден')

    user = db.query(UserProfile).filter(UserProfile.id == people.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    for people_key, people_value in people.dict().items():
        setattr(people_db, people_key, people_value)

    db.add(people_db)
    db.commit()
    db.refresh(people_db)
    return people_db


@people_router.delete('/{people_id}')
async def people_delete(people_id: int, current_user_id: int, db: Session = Depends(get_db)):
    people_db = db.query(GroupPeople).filter(GroupPeople.id == people_id).first()
    if people_db is None:
        raise HTTPException(status_code=404, detail='Такой информации нет')

    group = db.query(ChatGroup).filter(ChatGroup.id == people_db.group_id).first()
    user = db.query(UserProfile).filter(UserProfile.id == current_user_id).first()

    can_delete = (
            group.owner_id == current_user_id or
            user.user_status == StatusChoice.admin or
            people_db.user_id == current_user_id
    )

    if not can_delete:
        raise HTTPException(status_code=403, detail='Нет права высылать человека')

    db.delete(people_db)
    db.commit()
    return {'message': 'Deleted'}


@people_router.get('/group/{group_id}', response_model=List[GroupPeopleOutSchema])
async def people_by_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(ChatGroup).filter(ChatGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail='Группа не найдена')

    return db.query(GroupPeople).filter(GroupPeople.group_id == group_id).all()


@people_router.get('/user/{user_id}', response_model=List[GroupPeopleOutSchema])
async def groups_by_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Пользователь не найден')

    return db.query(GroupPeople).filter(GroupPeople.user_id == user_id).all()
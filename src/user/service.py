from enum import Enum

from sqlalchemy.orm import Session
from .models import User
from .schemas import UserPydantic
from src.dependencies import get_password_hash
from src.unit.models import Unit
from src.assessment.models import Assessment
from src.enrollment.models import Enrollment


def get_user_by_email(db: Session, email: str, no_password: bool = True):
    query = db.query(User)
    if no_password:
        query = query.filter(User.email == email).with_entities(User.email, User.role, User.faculty, User.monashId, User.monashObjectId, User.authcate, User.lastName, User.firstName)
    else:
        query = query.filter(User.email == email)
    db_user = query.all()

    if len(db_user) == 1:
        return db_user[0]
    else:
        print("Here's the user", db_user)
        return None


def create_user(db: Session, userData: UserPydantic):
    userData.role = userData.role.value
    userData.faculty = userData.faculty.value
    userData.monashObjectId = None
    db_user = User(**userData.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def signup_user(db: Session, userData: UserPydantic):
    db_user = db.query(User).filter(User.email == userData.email).all()
    if len(db_user) == 1:
        return False
    else:
        # hash the password
        userData.password = get_password_hash(userData.password)
        userData.role = userData.role.value
        userData.faculty = userData.faculty.value
        userData.monashObjectId = None
        return create_user(db, userData)


def get_users(db: Session):
    return db.query(User).all()


def update_user(db: Session, userData: UserPydantic, email: str):
    db_user = db.query(User).filter(User.email == email).all()
    print(db_user[0])
    if len(db_user) == 1:
        for field, value in userData.model_dump().items():
            print(field, value)
            if isinstance(getattr(User, field).type, Enum):
                value = getattr(User, field).type(value)
            setattr(db_user[0], field, value)

        db.commit()
        db.refresh(db_user)
        return db_user
    else:
        return None


def delete_user(db: Session, email: str):
    db_user = db.query(User).filter(User.email == email).all()
    if len(db_user) == 1:
        db.delete(db_user)
        db.commit()
        return True
    else:
        return False

def get_student_all_student_enrolled_units(db: Session, student_email: str):
    # Fetch the rows
    results = db.query(
        Unit.unitCode,
        Assessment.assessmentName,
        Assessment.id
    ).join(
        Enrollment, Enrollment.unitCode == Unit.unitCode
    ).join(
        Assessment, Unit.unitCode == Assessment.unitCode
    ).filter(
        Enrollment.userEmail == student_email
    ).all()

    # Process the results
    units = {}
    for unitCode, assessmentName, assessmentId in results:
        if unitCode not in units:
            units[unitCode] = {'unitCode': unitCode, 'assessments': []}
        units[unitCode]['assessments'].append({'assessmentName': assessmentName, 'id': assessmentId})

    return list(units.values())



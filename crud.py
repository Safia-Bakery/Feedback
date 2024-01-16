from sqlalchemy.orm import Session
import models
import pytz
from typing import Optional
import requests
from sqlalchemy.sql import func
from sqlalchemy import or_,and_,Date,cast
from datetime import datetime 

import models

def create_user(db:Session,tg_id,lang,sphere):
    db_user = models.HrUser(telegram_id=tg_id,lang=lang,sphere=sphere)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db:Session,tg_id):
    return db.query(models.HrUser).filter(models.HrUser.telegram_id == tg_id).first()

def update_user(db:Session,tg_id,lang,sphere):
    db_user = db.query(models.HrUser).filter(models.HrUser.telegram_id == tg_id).first()
    db_user.lang = lang
    db_user.sphere = sphere
    db.commit()
    db.refresh(db_user)
    return db_user

def create_request(db:Session,sphere,user_id,comments):
    query =models.HrRequest(sphere=sphere,user_id=user_id,comments=comments)
    db.add(query)
    db.commit()
    db.refresh(query)
    return query



def get_questions(db:Session, question):
    query  = db.query(models.HrQuestions)
    if question:
        query = query.filter(models.HrQuestions.question.ilike(f"%{question}%"))
    return query.all()
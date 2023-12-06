import json

from sqlalchemy.orm import Session

from .models import Highlight
from .schemas import DomMeta, HighlightPydantic, CompleteHighlight
from src.action.models import AnnotationActionPoint


localDatabase = []


def get_highlights_by_url(db: Session, url: str):
    db_highlights = db.query(Highlight).filter(Highlight.url == url).all()
    if db_highlights:
        for db_highlight in db_highlights:
            db_highlight.start_meta = DomMeta(**json.loads(db_highlight.start_meta))
            db_highlight.end_meta = DomMeta(**json.loads(db_highlight.end_meta))
    return db_highlights


def create_highlight(db: Session, highlight_data: CompleteHighlight):

    highlight = highlight_data.annotation
    start_meta = (highlight.startMeta.model_dump_json())
    end_meta = highlight.endMeta.model_dump_json()
    #check for feedback

    db_highlight = Highlight(id=str(highlight.id), startMeta=start_meta,
                             endMeta=end_meta, text=highlight.text, annotationTag=highlight.annotationTag.value,
                             notes=highlight.notes, feedbackId=str(highlight.feedbackId))


    db.add(db_highlight)

    db.commit()

    if highlight_data.actionItems:
        for action in highlight_data.actionItems:
            db_action= AnnotationActionPoint(action=action.action, category=action.category.value, deadline=action.deadline, highlightId=str(highlight.id) )
            db.add(db_action)

    db.commit()
    db.refresh(db_highlight)



def get_highlights(db: Session):
    return db.query(Highlight).all()


def get_highlight_tags(db: Session):
    return db.query(Highlight.annotation_tag).distinct().all()

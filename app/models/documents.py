
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from sqlalchemy.dialects.postgresql import JSONB
from .. import db, ma


class PDF(db.Model):
    __tablename__ = 'pdfs'
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(256), nullable=False)
    stored_path = db.Column(db.String(256), nullable=False, unique=True)
    sys_metadata = db.Column(JSONB, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    attachments = db.relationship('Attachment', backref='pdf', cascade='all, delete-orphan', lazy=True)

class Attachment(db.Model):
    __tablename__ = 'attachments'
    id = db.Column(db.Integer, primary_key=True)
    pdf_id = db.Column(db.Integer, db.ForeignKey('pdfs.id'), nullable=False)
    original_filename = db.Column(db.String(256), nullable=False)
    stored_path= db.Column(db.String(256), nullable=False, unique=True)
    sys_metadata = db.Column(JSONB, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class PDFSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PDF
        include_fk = True
        load_instance = True

class AttachmentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Attachment
        include_fk = True
        load_instance = True

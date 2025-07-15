import os
from flask import Blueprint, request, jsonify, current_app, abort, send_file
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from .. import db, file_manager
from ..models.documents import Attachment, AttachmentSchema, PDF
import json

attachment_bp = Blueprint('attachments', __name__)
attachment_schema = AttachmentSchema()

@attachment_bp.route('/<int:pdf_id>/', methods=['POST'])
def upload_attachment(pdf_id):
    current_app.logger.info(f"ATTACHMENT_BP | Upload request received for PDF ID: {pdf_id}")
    pdf = PDF.query.get_or_404(pdf_id)
    if 'file' not in request.files:
        current_app.logger.warning("ATTACHMENT_BP | No file part in request")
        abort(400, 'No file part')
    file = request.files['file']
    if file.filename == '':
        current_app.logger.warning("ATTACHMENT_BP | No selected file in upload")
        abort(400, 'No selected file')
    if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in current_app.config['ALLOWED_EXTENSIONS']:
        current_app.logger.warning(f"ATTACHMENT_BP | Unsupported file type attempted: {file.filename}")
        abort(400, 'Unsupported file type')

    user_meta = request.form.get('metadata')
    try:
        user_meta = json.loads(user_meta) if user_meta else {}
    except json.JSONDecodeError:
        current_app.logger.error("ATTACHMENT_BP | Invalid JSON in metadata")
        abort(400, 'Metadata must be valid JSON')

    stored_filename = file.filename
    tmp_path = os.path.join(current_app.config['TMP_DIRECTORY'], stored_filename)
    file.save(tmp_path)
    current_app.logger.info(f"ATTACHMENT_BP | File saved temporarily at {tmp_path}")

    try:
        query = Attachment.query.filter(
            and_(
                Attachment.original_filename.ilike(f"%{file.filename}%"),
                Attachment.pdf_id == pdf.id
            )
        )
        attachments = query.all()
        if len(attachments) != 0:
            current_app.logger.info(f"ATTACHMENT_BP | Existing attachment found for PDF ID {pdf_id}, deleting old record.")
            delete_attachment(attachment_id=attachments[0].id)
        storage_dir = f"{current_app.config['PARENT_DIRECTORY']}/{pdf.original_filename.split('.')[0]}/attachments"
        attachment = Attachment(
            pdf_id=pdf.id,
            original_filename=file.filename,
            stored_path=f"{storage_dir}/{stored_filename}",
            sys_metadata=user_meta
        )
        db.session.add(attachment)
        current_app.logger.info(f"ATTACHMENT_BP | New attachment record created for PDF ID {pdf_id}: {stored_filename}")
        db.session.commit()
        current_app.logger.info(f"ATTACHMENT_BP | Attachment committed to database for PDF ID {pdf_id}")
        file_manager.create_directory(path=storage_dir)
        file_manager.upload_file(local_path=tmp_path, storage_path=f"{storage_dir}/{stored_filename}")
        current_app.logger.info(f"ATTACHMENT_BP | File uploaded to storage: {storage_dir}/{stored_filename}")

    except Exception as e:
        current_app.logger.error(f"ATTACHMENT_BP | Database error during attachment upload: {e}")
        db.session.rollback()
        abort(500, str(e))
    os.remove(tmp_path)
    current_app.logger.info(f"ATTACHMENT_BP | Temporary file removed: {tmp_path}")
    return jsonify(attachment_schema.dump(attachment)), 201

@attachment_bp.route('/', methods=['GET'])
def list_attachments():
    pdf_id = request.args.get('pdf_id')
    name = request.args.get('name')
    meta_key = request.args.get('meta_key')
    meta_value = request.args.get('meta_value')
    current_app.logger.info(f"ATTACHMENT_BP | Listing attachments with filters - name: {name}, meta_key: {meta_key}, meta_value: {meta_value}")

    query = Attachment.query
    if pdf_id is not None:
        query = query.filter(Attachment.pdf_id == pdf_id)
    if name:
        query = query.filter(Attachment.original_filename.ilike(f"%{name}%"))
    if meta_key and meta_value:
        query = query.filter(Attachment.sys_metadata[meta_key].astext == meta_value)

    attachments = query.all()
    current_app.logger.info(f"ATTACHMENT_BP | Found {len(attachments)} attachments matching filters")
    return jsonify(attachment_schema.dump(attachments, many=True))

@attachment_bp.route('/download/<int:attachment_id>', methods=['GET'])
def download_pdf(attachment_id):
    current_app.logger.info(f"ATTACHMENT_BP | Download requested for attachment ID: {attachment_id}")
    attachment = Attachment.query.get_or_404(attachment_id)
    tmp_path = os.path.join(current_app.config['TMP_DIRECTORY'], attachment.original_filename)
    file_manager.download_file(src_path=attachment.stored_path, local_path=tmp_path)
    current_app.logger.info(f"ATTACHMENT_BP | Attachment downloaded to temporary path: {tmp_path}")
    return send_file(tmp_path, as_attachment=True, download_name=attachment.original_filename)

@attachment_bp.route('/<int:attachment_id>', methods=['GET'])
def get_attachment(attachment_id):
    current_app.logger.info(f"ATTACHMENT_BP | Fetching metadata for attachment ID: {attachment_id}")
    attachment = Attachment.query.get_or_404(attachment_id)
    return jsonify(attachment_schema.dump(attachment))

@attachment_bp.route('/<int:attachment_id>', methods=['DELETE'])
def delete_attachment(attachment_id):
    current_app.logger.info(f"ATTACHMENT_BP | Delete requested for attachment ID: {attachment_id}")
    attachment = Attachment.query.get_or_404(attachment_id)
    try:
        file_manager.delete_directory(attachment.stored_path)
        current_app.logger.info(f"ATTACHMENT_BP | Attachment file deleted from storage: {attachment.stored_path}")
        db.session.delete(attachment)
        db.session.commit()
        current_app.logger.info(f"ATTACHMENT_BP | Attachment record deleted from database: {attachment_id}")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"ATTACHMENT_BP | SQLAlchemy error during attachment deletion: {e}")
        abort(500, str(e))
    except Exception as e:
        current_app.logger.error(f"ATTACHMENT_BP | File deletion failed for attachment {attachment_id}: {e}")
        abort(500, f"File deletion failed: {e}")
    return jsonify({'message': 'PDF deleted successfully'}), 200

import json
import os

from flask import Blueprint, request, jsonify, current_app, abort, send_file
from sqlalchemy.exc import SQLAlchemyError

from .. import db, file_manager
from ..models.documents import PDF, PDFSchema

pdf_bp = Blueprint('pdfs', __name__)
pdf_schema = PDFSchema()

@pdf_bp.route('/', methods=['POST'])
def upload_pdf():
    current_app.logger.info(f" | PDF_BP |  | PDF_BP | PDF upload request received.")
    if 'file' not in request.files:
        current_app.logger.warning(f" | PDF_BP | No file part in request.")
        abort(400, 'No file part')
    file = request.files['file']
    if file.filename == '':
        current_app.logger.warning(f" | PDF_BP | No selected file in upload.")
        abort(400, 'No selected file')
    if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in current_app.config['ALLOWED_EXTENSIONS']:
        current_app.logger.warning(f" | PDF_BP | Unsupported file type attempted: {file.filename}")
        abort(400, 'Unsupported file type')

    user_meta = request.form.get('metadata')
    try:
        user_meta = json.loads(user_meta) if user_meta else {}
    except json.JSONDecodeError:
        current_app.logger.error(f" | PDF_BP | Invalid JSON in metadata.")
        abort(400, 'Metadata must be valid JSON')

    stored_filename = file.filename
    tmp_path = os.path.join(current_app.config['TMP_FOLDER'], stored_filename)
    file.save(tmp_path)
    current_app.logger.info(f" | PDF_BP | File saved temporarily at {tmp_path}")

    storage_dir = f"{current_app.config['PARENT_FOLDER']}/{file.filename.split('.')[0]}"
    file_manager.create_directory(path=storage_dir)
    file_manager.upload_file(local_path=tmp_path, storage_path=f"{storage_dir}/{stored_filename}")
    current_app.logger.info(f" | PDF_BP | File uploaded to storage: {storage_dir}/{stored_filename}")

    pdf = PDF(
        original_filename=file.filename,
        stored_path=f"{storage_dir}/{stored_filename}",
        sys_metadata=user_meta
    )
    try:
        query = PDF.query.filter(PDF.original_filename.ilike(f"%{stored_filename}%"))
        pdfs = query.all()
        if len(pdfs) == 0:
            db.session.add(pdf)
            current_app.logger.info(f" | PDF_BP | New PDF record created: {stored_filename}")
        else:
            current_app.logger.info(f" | PDF_BP | Existing PDF found, deleting old record for: {stored_filename}")
            delete_pdf(pdf_id=pdfs[0].id)
        db.session.commit()
        current_app.logger.info(f" | PDF_BP | PDF committed to database: {stored_filename}")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f" | PDF_BP | Database error during PDF upload: {e}")
        abort(500, str(e))
    os.remove(tmp_path)
    current_app.logger.info(f" | PDF_BP | Temporary file removed: {tmp_path}")
    return jsonify(pdf_schema.dump(pdf)), 201

@pdf_bp.route('/', methods=['GET'])
def list_pdfs():
    name = request.args.get('name', "")
    meta_key = request.args.get('meta_key')
    meta_value = request.args.get('meta_value')
    current_app.logger.info(f" | PDF_BP | Listing PDFs with filters - name: {name}, meta_key: {meta_key}, meta_value: {meta_value}")

    query = PDF.query
    if name:
        query = query.filter(PDF.original_filename.ilike(f"%{name}%"))
    if meta_key and meta_value:
        query = query.filter(PDF.sys_metadata[meta_key].astext == meta_value)

    pdfs = query.all()
    current_app.logger.info(f" | PDF_BP | Found {len(pdfs)} PDFs matching filters.")
    return jsonify(pdf_schema.dump(pdfs, many=True))

@pdf_bp.route('/download/<int:pdf_id>', methods=['GET'])
def download_pdf(pdf_id):
    current_app.logger.info(f" | PDF_BP | Download requested for PDF ID: {pdf_id}")
    pdf = PDF.query.get_or_404(pdf_id)
    tmp_path = os.path.join(current_app.config['TMP_FOLDER'], pdf.original_filename)
    file_manager.download_file(src_path=pdf.stored_path, local_path=tmp_path)
    current_app.logger.info(f" | PDF_BP | PDF downloaded to temporary path: {tmp_path}")
    return send_file(tmp_path, as_attachment=True, download_name=pdf.original_filename)

@pdf_bp.route('/<int:pdf_id>', methods=['GET'])
def get_pdf(pdf_id):
    current_app.logger.info(f" | PDF_BP | Fetching metadata for PDF ID: {pdf_id}")
    pdf = PDF.query.get_or_404(pdf_id)
    return jsonify(pdf_schema.dump(pdf))

@pdf_bp.route('/<int:pdf_id>', methods=['DELETE'])
def delete_pdf(pdf_id):
    current_app.logger.info(f" | PDF_BP | Delete requested for PDF ID: {pdf_id}")
    pdf = PDF.query.get_or_404(pdf_id)
    try:
        storage_dir = f"{current_app.config['PARENT_FOLDER']}/{pdf.original_filename.split('.')[0]}"
        file_manager.delete_directory(storage_dir)
        current_app.logger.info(f" | PDF_BP | PDF file deleted from storage: {storage_dir}")
        db.session.delete(pdf)
        db.session.commit()
        current_app.logger.info(f" | PDF_BP | PDF record deleted from database: {pdf_id}")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f" | PDF_BP | SQLAlchemy error during PDF deletion: {e}")
        abort(500, str(e))
    except Exception as e:
        current_app.logger.error(f" | PDF_BP | File deletion failed for PDF {pdf_id}: {e}")
        abort(500, f"File deletion failed: {e}")
    return jsonify({'message': 'PDF deleted successfully'}), 200

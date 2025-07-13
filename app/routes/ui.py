import os
import shutil

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, current_app
from werkzeug.utils import secure_filename

from .pdfs import pdf_schema, download_pdf
from ..models.documents import PDF
import requests

ui_bp = Blueprint('ui', __name__)
API_PREFIX = '/api'

@ui_bp.route('/')
def index():
    current_app.logger.info('UI: Index page accessed.')
    pdfs = PDF.query.all()
    current_app.logger.info(f'UI: Retrieved {len(pdfs)} PDFs for index page.')
    return render_template('index.html', pdfs=pdfs, many=True)

@ui_bp.route('/pdf/<int:pdf_id>')
def view_pdf(pdf_id):
    current_app.logger.info(f'UI: View PDF requested for PDF ID: {pdf_id}')
    pdf = PDF.query.get_or_404(pdf_id)
    download_pdf(pdf_id=pdf_id)
    tmp_path = os.path.join(current_app.config['TMP_FOLDER'], pdf.original_filename)
    static_path = os.path.join(current_app.config['STATIC_FOLDER'], pdf.original_filename)
    shutil.copy(tmp_path, static_path)
    current_app.logger.info(f'UI: Copied PDF to static path: {static_path}')
    return render_template('view_pdf.html', pdf=pdf, pdf_file_url=url_for('static', filename=pdf.original_filename))

@ui_bp.route('/upload/pdf', methods=['GET', 'POST'])
def upload_pdf_ui():
    if request.method == 'POST':
        file = request.files.get('file')
        metadata = request.form.get('metadata')
        if not file:
            current_app.logger.warning('UI: No file selected for PDF upload.')
            flash('No file selected', 'danger')
            return redirect(request.url)
        url = url_for('pdfs.upload_pdf', _external=True)
        data = {'metadata': metadata or '{}'}
        files = {'file': (secure_filename(file.filename), file.stream, 'application/pdf')}
        current_app.logger.info(f'UI: Sending PDF upload to API for file: {file.filename}')
        resp = requests.post(url, data=data, files=files)
        if resp.status_code == 201:
            current_app.logger.info('UI: PDF uploaded successfully via API.')
            flash('PDF uploaded', 'success')
            return redirect(url_for('ui.index'))
        current_app.logger.error(f'UI: PDF upload failed with status {resp.status_code}: {resp.text}')
        flash(f'Error: {resp.text}', 'danger')
    return render_template('upload_pdf.html')

@ui_bp.route('/upload/attachment/<int:pdf_id>', methods=['GET', 'POST'])
def upload_attachment_ui(pdf_id):
    pdf = PDF.query.get_or_404(pdf_id)
    if request.method == 'POST':
        file = request.files.get('file')
        metadata = request.form.get('metadata')
        if not file:
            current_app.logger.warning(f'UI: No file selected for attachment upload to PDF ID {pdf_id}.')
            flash('No file selected', 'danger')
            return redirect(request.url)
        url = url_for('attachments.upload_attachment', pdf_id=pdf_id, _external=True)
        data = {'metadata': metadata or '{}'}
        files = {'file': (secure_filename(file.filename), file.stream, file.mimetype)}
        current_app.logger.info(f'UI: Sending attachment upload to API for file: {file.filename} (PDF ID: {pdf_id})')
        resp = requests.post(url, data=data, files=files)
        if resp.status_code == 201:
            current_app.logger.info(f'UI: Attachment uploaded successfully to PDF ID {pdf_id}.')
            flash('Attachment uploaded', 'success')
            return redirect(url_for('ui.view_pdf', pdf_id=pdf_id))
        current_app.logger.error(f'UI: Attachment upload failed with status {resp.status_code}: {resp.text}')
        flash(f'Error: {resp.text}', 'danger')
    return render_template('upload_attachment.html', pdf=pdf_schema.dump(pdf))

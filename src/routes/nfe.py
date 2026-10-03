from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import tempfile
import shutil
import os

from db import obter_ip_cliente, registrar_processamento

nfe_bp = Blueprint('nfe', __name__)

ALLOWED_EXTENSIONS = {'xml'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@nfe_bp.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400

        files = request.files.getlist('files')

        if not files or files[0].filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

        # Criar diretório temporário para os uploads
        temp_dir = tempfile.mkdtemp()
        uploaded_files = []

        try:
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(temp_dir, filename)
                    file.save(file_path)
                    uploaded_files.append(file_path)

            if not uploaded_files:
                return jsonify({'error': 'Nenhum arquivo XML válido foi enviado'}), 400

            # Processar os arquivos XML
            from nfe_processor import NFEProcessor
            processor = NFEProcessor()
            buffer, filename, quantidade_notas = processor.process_files(uploaded_files)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        try:
            registrar_processamento(
                ip_origem=obter_ip_cliente(request),
                quantidade_notas=quantidade_notas
            )
        except Exception as e:
            current_app.logger.warning(f"Falha ao registrar histórico: {e}")
            # o histórico é acessório — não deve derrubar o processamento se o banco falhar

        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': f'Erro ao processar arquivos: {str(e)}'}), 500

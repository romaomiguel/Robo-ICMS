let selectedFiles = [];

        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const processBtn = document.getElementById('processBtn');
        const clearBtn = document.getElementById('clearBtn');
        const message = document.getElementById('message');
        const progressBar = document.getElementById('progressBar');
        const progressFill = document.getElementById('progressFill');
        const loading = document.getElementById('loading');

        // Upload area click
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });

        function handleFiles(files) {
            for (let file of files) {
                if (file.name.toLowerCase().endsWith('.xml')) {
                    if (!selectedFiles.some(f => f.name === file.name)) {
                        selectedFiles.push(file);
                    }
                } else {
                    showMessage('Apenas arquivos XML são aceitos!', 'error');
                }
            }
            updateFileList();
            updateProcessButton();
        }

        function updateFileList() {
            fileList.innerHTML = '';
            selectedFiles.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <div>
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatFileSize(file.size)}</div>
                    </div>
                    <button class="remove-file" onclick="removeFile(${index})">×</button>
                `;
                fileList.appendChild(fileItem);
            });
        }

        function removeFile(index) {
            selectedFiles.splice(index, 1);
            updateFileList();
            updateProcessButton();
        }

        function clearFiles() {
            selectedFiles = [];
            fileInput.value = '';
            updateFileList();
            updateProcessButton();
            hideMessage();
        }

        function updateProcessButton() {
            processBtn.disabled = selectedFiles.length === 0;
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        function showMessage(text, type) {
            message.textContent = text;
            message.className = `message ${type}`;
            message.style.display = 'block';
        }

        function hideMessage() {
            message.style.display = 'none';
        }

        function showLoading() {
            loading.style.display = 'flex';
            processBtn.disabled = true;
            clearBtn.disabled = true;
        }

        function hideLoading() {
            loading.style.display = 'none';
            processBtn.disabled = false;
            clearBtn.disabled = false;
        }

        async function processFiles() {
            if (selectedFiles.length === 0) {
                showMessage('Selecione pelo menos um arquivo XML!', 'error');
                return;
            }

            const formData = new FormData();
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            showLoading();
            hideMessage();

            try {
                const response = await fetch('/api/nfe/upload', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const blob = await response.blob();

                    const disposition = response.headers.get('Content-Disposition') || '';
                    const match = disposition.match(/filename="?([^"]+)"?/);
                    const filename = match ? match[1] : 'resultado.xlsx';

                    const url = window.URL.createObjectURL(blob);

                    showMessage(
                        `Processados ${selectedFiles.length} arquivo(s) XML com sucesso`,
                        'success'
                    );

                    // Add download link
                    const downloadLink = document.createElement('a');
                    downloadLink.href = url;
                    downloadLink.className = 'download-link';
                    downloadLink.textContent = '📥 Baixar Planilha';
                    downloadLink.download = filename;

                    message.appendChild(document.createElement('br'));
                    message.appendChild(downloadLink);

                } else {
                    const result = await response.json();
                    showMessage(result.error || 'Erro ao processar arquivos', 'error');
                }
            } catch (error) {
                showMessage('Erro de conexão: ' + error.message, 'error');
            } finally {
                hideLoading();
            }
        }
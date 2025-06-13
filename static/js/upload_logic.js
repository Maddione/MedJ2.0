document.addEventListener('DOMContentLoaded', function() {
    const uploadContainer = document.getElementById('upload-container');
    const categorySelect = document.getElementById('category');
    const specialistSelect = document.getElementById('specialist');
    const fileInput = document.getElementById('file_input');
    const uploadOcrButton = document.getElementById('upload-ocr-button');
    const analyzeButton = document.getElementById('analyze-button');
    const ocrTextArea = document.getElementById('ocr_text_area');

    const step2UploadDiv = document.getElementById('step2-upload');
    const step3ReviewDiv = document.getElementById('step3-review');

    const resultsSection = document.getElementById('results-section');
    const resultSummary = document.getElementById('result-summary');
    const resultHtmlTable = document.getElementById('result-html-table');

    const imagePreview = document.getElementById('image-preview');
    const pdfPreview = document.getElementById('pdf-preview');

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    function checkStep1() {
        if (categorySelect.value && specialistSelect.value) {
            step2UploadDiv.style.display = 'flex';
        } else {
            step2UploadDiv.style.display = 'none';
        }
    }

    function handleFileSelection() {
        if (fileInput.files.length > 0) {
            uploadOcrButton.disabled = false;
            const file = fileInput.files[0];
            const reader = new FileReader();

            reader.onload = function(e) {
                if (file.type === "application/pdf") {
                    pdfPreview.src = e.target.result;
                    pdfPreview.style.display = 'block';
                    imagePreview.style.display = 'none';
                } else {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                    pdfPreview.style.display = 'none';
                }
            };
            reader.readAsDataURL(file);
        } else {
            uploadOcrButton.disabled = true;
        }
    }

    categorySelect.addEventListener('change', checkStep1);
    specialistSelect.addEventListener('change', checkStep1);
    fileInput.addEventListener('change', handleFileSelection);

    uploadOcrButton.addEventListener('click', function() {
        uploadOcrButton.disabled = true;
        uploadOcrButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Обработка...`;

        const formData = new FormData();
        formData.append('document', fileInput.files[0]);

        fetch('/perform-ocr/', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            body: formData
        })
        .then(response => {
            if (!response.ok) { throw new Error('Network response was not ok.'); }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                ocrTextArea.value = data.ocr_text;
                step3ReviewDiv.style.display = 'block';
                document.getElementById('step1-selection').style.display = 'none';
                document.getElementById('step2-upload').style.display = 'none';
            } else {
                alert('Грешка при OCR: ' + data.message);
            }
        })
        .catch(error => {
            console.error('OCR Error:', error);
            alert('Критична грешка при OCR обработката.');
        })
        .finally(() => {
            uploadOcrButton.disabled = false;
            uploadOcrButton.textContent = 'Качи за OCR';
        });
    });

    analyzeButton.addEventListener('click', function() {
        analyzeButton.disabled = true;
        analyzeButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Анализ с AI...`;

        const dataToSend = {
            edited_text: ocrTextArea.value,
            category: categorySelect.value,
            specialist: specialistSelect.value,
        };

        fetch('/analyze-document/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(dataToSend)
        })
        .then(response => {
            if (!response.ok) { throw new Error('Network response was not ok.'); }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                resultSummary.innerHTML = `<p class="mb-0">${data.summary}</p>`;
                resultHtmlTable.innerHTML = data.html_table;
                resultsSection.style.display = 'block';
                uploadContainer.style.display = 'none';
            } else {
                alert('Грешка при анализ: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Analyze Error:', error);
            alert('Критична грешка при финалния анализ.');
        })
        .finally(() => {
            analyzeButton.disabled = false;
            analyzeButton.textContent = 'Одобри и анализирай с AI';
        });
    });
});
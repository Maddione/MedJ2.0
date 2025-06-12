document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const docKind = document.getElementById('doc_kind');
    const fileType = document.getElementById('file_type');
    const fileInput = document.getElementById('file_input');
    const uploadButton = document.getElementById('upload-button');
    const resultsSection = document.getElementById('results-section');
    const resultSummary = document.getElementById('result-summary');
    const resultHtmlTable = document.getElementById('result-html-table');

    function validateForm() {
        const isDocKindSelected = docKind.value !== "";
        const isFileTypeSelected = fileType.value !== "";
        const isFileSelected = fileInput.files.length > 0;
        uploadButton.disabled = !(isDocKindSelected && isFileTypeSelected && isFileSelected);
    }

    docKind.addEventListener('change', validateForm);
    fileType.addEventListener('change', validateForm);
    fileInput.addEventListener('change', validateForm);

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
        uploadButton.disabled = true;
        uploadButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Обработка...`;
        resultsSection.style.display = 'none';

        // FormData взима CSRF токена автоматично от input полето във формата
        const formData = new FormData(uploadForm);

        fetch(uploadForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                // CSRF токенът се изпраща, но без Django да го обработва в JS
                // Django го взима от formData, стига да е във формата
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                resultSummary.innerHTML = `<p class="mb-0">${data.summary}</p>`;
                resultHtmlTable.innerHTML = data.html_table;
                resultsSection.style.display = 'block';
            } else {
                alert("Грешка: " + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const errorMessage = error.message || "Възникна критична грешка.";
            alert(errorMessage);
        })
        .finally(() => {
            uploadButton.disabled = false;
            uploadButton.textContent = "Качи и анализирай";
        });
    });
});
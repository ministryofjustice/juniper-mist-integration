document.addEventListener('DOMContentLoaded', function() {
    var select = document.getElementById('csvSelect');

    fetch('/lookup/data-src')
        .then(response => response.json())
        .then(csvFiles => {
            csvFiles.forEach(file => {
                var option = document.createElement('option');
                option.textContent = file;
                select.appendChild(option);
            });
        })
        .catch(error => console.error('Error fetching CSV files:', error));
});
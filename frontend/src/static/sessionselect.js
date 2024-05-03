document.addEventListener('DOMContentLoaded', function() {
    var select = document.getElementById('csvSelect');

    fetch('/lookup/data-src/csv')
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

document.addEventListener('DOMContentLoaded', function() {
    var select = document.getElementById('envSelect');

fetch('/lookup/data-src/env')
    .then(response => response.json())
    .then(envFiles => {
        console.log('Files from API:', envFiles); // Log the files received from the API
        envFiles.forEach(file => {
            console.log('Adding file to dropdown:', file); // Log each file being added to the dropdown
            var option = document.createElement('option');
            option.textContent = file;
            select.appendChild(option);
        });
    })
    .catch(error => console.error('Error fetching ENV files:', error));
});

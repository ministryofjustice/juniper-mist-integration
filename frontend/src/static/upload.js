function uploadFile() {
    var fileInput = document.getElementById('file-upload-1');
    var file = fileInput.files[0]

    var formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        console.log(data);
        alert('File upload successfull - congrats.');
    })
    .catch(error => {
        console.error('There was a problemo', error);
        alert('There was a problemo');
    });
}
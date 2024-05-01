function uploadFile() {
    var fileInput = document.getElementById('file-upload-1');
    
    if (fileInput !== null) {
        if (fileInput.files.length > 0) {
            var file = fileInput.files[0];
            console.log('File selected:', file.name);

        } else {
            console.error('No files found.');

        }
    } else {
        console.error('File input element not found');
    }
}
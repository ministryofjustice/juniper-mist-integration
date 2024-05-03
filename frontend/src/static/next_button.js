function sessionSelect(selected_env_file, selected_csv_file) {
    // Create a FormData object
    var formData = new FormData();

    // Append the CSV file name
    formData.append('csv_file', selected_csv_file);

    // Append the environment file name (if applicable)
    // Uncomment the line below and replace 'selectedEnv' with the actual value from session select for environment file
    formData.append('env_file', selected_env_file);

    // Make the POST request
    fetch('/submit', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        window.location.href = '/interactive-shell';
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}


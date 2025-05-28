<script>
    // JavaScript for handling image upload and tumor detection
    function detectTumor(event) {
        // Prevent form submission to stay on the page
        event.preventDefault();

        // Get the uploaded file
        const fileInput = document.getElementById('fileInput');
        const file = fileInput.files[0];

        if (file) {
            // Display the uploaded image
            const imagePreview = document.getElementById('imagePreview');
            imagePreview.innerHTML = `<img id="uploadedImage" src="${URL.createObjectURL(file)}" alt="Uploaded Image" style="max-width: 100%; height: auto;">`;
            imagePreview.style.display = 'block'; // Show the image container
        } else {
            alert("Please select an image file.");
        }
    }
</script>

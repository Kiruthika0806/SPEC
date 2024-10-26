document.getElementById('image-upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch('/upload-image/', {
        method: 'POST',
        body: formData,
    });
    const imageBlob = await response.blob();
    const imgElement = document.createElement('img');
    imgElement.src = URL.createObjectURL(imageBlob);
    document.getElementById('image-preview').innerHTML = '';
    document.getElementById('image-preview').appendChild(imgElement);
});

document.getElementById('base64-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('text').value;
    const response = await fetch('/encode-base64/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
    });
    const result = await response.json();
    document.getElementById('base64-result').innerText = `Base64 Encoded: ${result.base64_encoded_text}`;
});

document.getElementById('audio-fast-forward-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch('/fast-forward-audio/', {
        method: 'POST',
        body: formData,
    });
    const audioBlob = await response.blob();
    const audioElement = document.createElement('audio');
    audioElement.controls = true;
    audioElement.src = URL.createObjectURL(audioBlob);
    document.getElementById('audio-preview').innerHTML = '';
    document.getElementById('audio-preview').appendChild(audioElement);
});

let mediaRecorder;
let audioChunks = [];

// Fungsi untuk memulai perekaman
async function startRecording() {
    const nameInput = document.getElementById("namaInput").value; 
    
    if (!nameInput) {
        alert("Harap masukkan nama penghafal sebelum merekam.");
        location.reload();  
        return;  
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    const startButton = document.querySelector('.btn-success');
    const stopButton = document.querySelector('.btn-danger');
    startButton.innerText = 'Sedang Merekam...';
    startButton.classList.add('disabled');
    stopButton.classList.remove('disabled');
    startButton.classList.add('recording');

    mediaRecorder.ondataavailable = function(event) {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async function() {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        document.getElementById('audioPlayback').src = audioUrl;

        const namaInput = document.getElementById('namaInput').value;
        if (!namaInput) {
            alert("Harap masukkan nama hafalan sebelum merekam.");
            return;
        }

        const filename = `${namaInput.replace(/\s+/g, '_')}_hafalan_${Date.now()}.wav`;

        const formData = new FormData();
        formData.append('file', audioBlob, filename);

        const response = await fetch('/save_audio', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (data.filename) {
            const audioList = document.getElementById('audioList');
            const newRow = document.createElement('tr');
            newRow.setAttribute('id', `row-${data.filename}`);
            newRow.classList.add('audio-row'); 
            
            newRow.innerHTML = `
                <td>${data.filename}</td>
                <td class="audio-row">
                    <audio controls>
                        <source src="uploads/${data.filename}" type="audio/wav">
                    </audio>
                    <button class="btn btn-danger" onclick="deleteAudio('${data.filename}')">Hapus</button>
                </td>
            `;
            audioList.appendChild(newRow);
            
            location.reload();  
        }

        startButton.innerText = 'Mulai Rekam';
        startButton.classList.remove('disabled');
        stopButton.classList.add('disabled');
        audioChunks = [];  
    };
}

// Fungsi untuk menghentikan perekaman
function stopRecording() {
    mediaRecorder.stop();
}

// Fungsi untuk menghapus audio
function deleteAudio(filename) {
    fetch(`/delete_audio/${filename}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Audio deleted successfully!') {
            const rowToDelete = document.getElementById(`row-${filename}`);
            rowToDelete.remove();
        }
    });
}

// Fungsi untuk mengunggah file berformat .wav
document.getElementById('uploadButton').addEventListener('click', function() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        alert("Harap pilih file untuk diunggah.");
        return;
    }

    const fileType = file.type;
    if (fileType !== "audio/wav") {
        alert("Hanya file berformat .wav yang diizinkan.");
        window.location.reload(); // Refresh halaman setelah alert ditutup
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/save_audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.filename) {
            const audioList = document.getElementById('audioList');
            const newRow = document.createElement('tr');
            newRow.setAttribute('id', `row-${data.filename}`);
            
            newRow.innerHTML = `
                <td>${data.filename}</td>
                <td class="audio-row">
                    <audio controls>
                        <source src="uploads/${data.filename}" type="audio/wav">
                    </audio>
                    <button class="btn btn-danger" onclick="deleteAudio('${data.filename}')">Hapus</button>
                </td>
            `;
            audioList.appendChild(newRow);

            window.location.reload(); // Halaman akan di-refresh otomatis setelah upload
        }
    })
    .catch(error => console.error('Error:', error));
});

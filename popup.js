document.addEventListener('DOMContentLoaded', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        let url = tabs[0].url;
        if (url && url.includes('youtube.com/watch')) {
            const urlInput = document.getElementById('video-id');
            urlInput.value = url;
            urlInput.classList.add('highlight');
            
            setTimeout(() => {
                urlInput.classList.remove('highlight');
            }, 2000);
        }
    });
});

document.getElementById('submit').addEventListener('click', async () => {
    let videoInput = document.getElementById('video-id').value;
    const query = document.getElementById('query').value;
  
    if (videoInput && query) {
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('response').innerHTML = '';

        const videoId = extractVideoId(videoInput);
        // Use the live URL instead of localhost
        // http://127.0.0.1:8000
        // https://youtube-video-chat.onrender.com/
        // uvicorn server:app --reload
        try {
            const response = await fetch('http://127.0.0.1:8000/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_id: videoId, query: query })
            });
            
            const data = await response.json();
            document.getElementById('response').innerHTML = `<p>Answer: ${data.answer}</p>
                ${data.timestamp_url ? `<a href="${data.timestamp_url}" target="_blank">Go to Timestamp</a>` : ''}`;
        } catch (error) {
            document.getElementById('response').innerHTML = 'An error occurred. Please try again.';
        } finally {
            document.getElementById('loading').style.display = 'none';
        }
    }
});

function extractVideoId(input) {
    const urlPattern = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = input.match(urlPattern);
    return match ? match[1] : input;
}
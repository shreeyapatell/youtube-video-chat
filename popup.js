document.getElementById('submit').addEventListener('click', async () => {
    let videoInput = document.getElementById('video-id').value;
    const query = document.getElementById('query').value;
  
    if (videoInput && query) {
        // Extract video ID if a full YouTube URL is provided
        const videoId = extractVideoId(videoInput);
  
        // Use the live URL instead of localhost
        // http://127.0.0.1:8000
        // https://youtube-video-chat.onrender.com/
        // uvicorn server:app --reload
        const response = await fetch('https://youtube-video-chat.onrender.com/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_id: videoId, query: query })
        });
        
        const data = await response.json();
        document.getElementById('response').innerHTML = `<p>Answer: ${data.answer}</p>
            ${data.timestamp_url ? `<a href="${data.timestamp_url}" target="_blank">Go to Timestamp</a>` : ''}`;
    }
  });
  
  // Function to extract video ID from a full YouTube URL or handle a raw ID
  function extractVideoId(input) {
      const urlPattern = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
      const match = input.match(urlPattern);
      return match ? match[1] : input;  // If no match, assume input is a raw video ID
  }
  
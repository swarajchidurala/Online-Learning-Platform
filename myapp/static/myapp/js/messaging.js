function deleteMessage(msgId) {
    if (!confirm("Are you sure you want to delete this message?")) return;

    fetch('/api/delete_message/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ message_id: msgId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Reload page to reflect changes
                window.location.reload();
            } else {
                alert("Error deleting message: " + (data.error || "Unknown error"));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert("An error occurred while deleting the message.");
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

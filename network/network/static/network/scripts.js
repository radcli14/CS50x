document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded');

    const follow_button = document.querySelector('#follow-button');
    if (follow_button) {
        follow_button.addEventListener('click', follow);
    }

});

function follow(event) {
    const username = event.target.dataset.username;
    const textContent = event.target.textContent.trim();
    console.log(`${textContent} button clicked for user: ${username}`);
    fetch(`/follow/${username}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Update button text and follower count
        if (data.status === 'followed') {
            event.target.textContent = 'Unfollow';
        } else if (data.status === 'unfollowed') {
            event.target.textContent = 'Follow';
        }
        document.querySelector('#follower-count').textContent = data.follower_count;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

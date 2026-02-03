document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded');

    const follow_button = document.querySelector('#follow-button');
    if (follow_button) {
        follow_button.addEventListener('click', follow);
    }

    const edit_buttons = document.querySelectorAll('.edit-post');
    edit_buttons.forEach(button => {
        button.addEventListener('click', edit);
    });
});

/// Respond to clicking the Edit button on a post
function edit() {
    console.log('Edit button clicked for post id:', this.dataset.id);
    const postId = this.dataset.id;
    const postContent = document.querySelector(`#post-content-${postId}`);
    const editForm = document.querySelector(`#edit-post-${postId}`);
    if (editForm.style.display === 'block') {
        postContent.style.display = 'block';
        editForm.style.display = 'none';
    } else {
        postContent.style.display = 'none';
        editForm.style.display = 'block';
    }
}

/// Follow or unfollow a user based on what is currently onscreen
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

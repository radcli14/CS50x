document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded');

    const follow_button = document.querySelector('#follow-button');
    if (follow_button) {
        follow_button.addEventListener('click', follow);
    }

    // Listeners for the edit buttons
    document.querySelectorAll('.edit-post').forEach(button => {
        button.addEventListener('click', edit);
    });

    // Listeners for the save buttons inside the edit forms
    document.querySelectorAll('.save-post').forEach(button => {
        const parentForm = button.closest('.edit-post-form');
        button.addEventListener('click', function() {
            save(parentForm.dataset.id);
        });
    });
});

/// Respond to clicking the Edit button on a post
function edit() {
    console.log('Edit button clicked for post id:', this.dataset.id);
    const postId = this.dataset.id;
    const postContent = document.querySelector(`#post-content-${postId}`);
    const editForm = document.querySelector(`#edit-post-${postId}`);
    
    if (editForm.style.display === 'block') {
        // Form was open and editable, now closing it
        postContent.style.display = 'block';
        editForm.style.display = 'none';
    } else {
        // Form was closed, now opening it for editing
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

/// When save button is clicked, update the content and hide the edit form
function save(postId) {
    console.log('Save button clicked for post id:', postId);
    const postContent = document.querySelector(`#post-content-${postId}`);
    const editForm = document.querySelector(`#edit-post-${postId}`);

    // Set the postContent to whats in the edit form, and then toggle visibility
    const newContent = document.querySelector(`#textarea-${postId}`).value.trim();
    console.log("New content to save:", newContent);
    postContent.innerHTML = newContent;
    postContent.style.display = 'block';
    editForm.style.display = 'none';
}
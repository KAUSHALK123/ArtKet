// ArtConnect JavaScript functionality

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Social features
function toggleLike(postId) {
    fetch(`/api/posts/${postId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const heartIcon = document.querySelector(`[onclick="toggleLike(${postId})"] i`);
            if (data.liked) {
                heartIcon.className = 'fas fa-heart fa-lg text-danger';
                showAlert('Post liked!', 'success');
            } else {
                heartIcon.className = 'far fa-heart fa-lg';
                showAlert('Post unliked', 'info');
            }
        } else {
            showAlert(data.error || 'Failed to like post', 'danger');
        }
    })
    .catch(error => {
        showAlert('An error occurred', 'danger');
    });
}

function showComments(postId) {
    // Create a modal or expand comments section
    const commentText = prompt('Add a comment:');
    if (commentText && commentText.trim()) {
        fetch(`/api/posts/${postId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content: commentText.trim() })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Comment added!', 'success');
                // In a real app, we'd update the UI to show the new comment
            } else {
                showAlert(data.error || 'Failed to add comment', 'danger');
            }
        })
        .catch(error => {
            showAlert('An error occurred', 'danger');
        });
    }
}

function showCreatePost() {
    // Simple implementation - in a real app this would be a modal with file upload
    const imageUrl = prompt('Enter image URL:');
    const caption = prompt('Enter caption (or leave empty for AI generation):');
    
    if (imageUrl && imageUrl.trim()) {
        const postData = {
            image_url: imageUrl.trim(),
            caption: caption || '',
            hashtags: '',
            story: ''
        };
        
        // If no caption provided, generate with AI
        if (!caption || !caption.trim()) {
            const description = prompt('Briefly describe your artwork for AI caption generation:');
            if (description) {
                generateAICaption(description, postData);
                return;
            }
        }
        
        createPost(postData);
    }
}

function generateAICaption(description, postData) {
    fetch('/api/ai/generate-caption', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image_description: description })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            postData.caption = data.caption;
            postData.hashtags = data.hashtags;
            postData.story = data.story;
            showAlert('AI generated amazing content for your post!', 'success');
        }
        createPost(postData);
    })
    .catch(error => {
        showAlert('AI generation failed, proceeding with basic post', 'warning');
        createPost(postData);
    });
}

function createPost(postData) {
    fetch('/api/posts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Post created successfully!', 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showAlert(data.error || 'Failed to create post', 'danger');
        }
    })
    .catch(error => {
        showAlert('An error occurred', 'danger');
    });
}

// Marketplace features
function showMarketplace() {
    window.location.href = '/marketplace';
}

function showCart() {
    window.location.href = '/cart';
}

// Following functionality
function toggleFollow(userId) {
    fetch(`/api/follow/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const followButtons = document.querySelectorAll(`[onclick="toggleFollow(${userId})"]`);
            followButtons.forEach(button => {
                if (data.following) {
                    button.innerHTML = '<i class="fas fa-user-check"></i> Following';
                    button.className = 'btn btn-sm btn-success';
                    showAlert('Now following this artisan!', 'success');
                } else {
                    button.innerHTML = '<i class="fas fa-user-plus"></i> Follow';
                    button.className = 'btn btn-sm btn-outline-primary';
                    showAlert('Unfollowed artisan', 'info');
                }
            });
        } else {
            showAlert(data.error || 'Failed to follow/unfollow', 'danger');
        }
    })
    .catch(error => {
        showAlert('An error occurred', 'danger');
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('ArtConnect app initialized');
});
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
    // TODO: Implement like functionality
    console.log('Like post:', postId);
    showAlert('Like functionality coming soon!', 'info');
}

function showComments(postId) {
    // TODO: Implement comments functionality
    console.log('Show comments for post:', postId);
    showAlert('Comments functionality coming soon!', 'info');
}

function showCreatePost() {
    // TODO: Implement create post functionality
    showAlert('Create post functionality coming soon!', 'info');
}

// Marketplace features
function showMarketplace() {
    // TODO: Implement marketplace page
    showAlert('Marketplace functionality coming soon!', 'info');
}

function showCart() {
    // TODO: Implement cart functionality
    showAlert('Cart functionality coming soon!', 'info');
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('ArtConnect app initialized');
});
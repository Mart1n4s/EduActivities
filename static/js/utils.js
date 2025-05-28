console.log('Utils script loaded');

function showError(message, formElement) {
    showAlert(message, 'danger', formElement);
}

function showSuccess(message, formElement) {
    showAlert(message, 'success', formElement);
}

function showAlert(message, type, formElement) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade show mt-3`;
    alertDiv.innerHTML = message;
    formElement.insertAdjacentElement('beforebegin', alertDiv);

    setTimeout(() => {
        alertDiv.classList.remove('show');
        alertDiv.classList.add('fade');
        setTimeout(() => {
            alertDiv.remove();
        }, 500); 
    }, 1500);
} 
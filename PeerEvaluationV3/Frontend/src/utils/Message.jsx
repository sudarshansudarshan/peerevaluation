export const showMessage = (message, type = 'info') => {
    const messageBox = document.createElement('div');
    messageBox.textContent = message;
    messageBox.style.position = 'fixed';
    messageBox.style.top = '20px';
    messageBox.style.left = '50%';
    messageBox.style.transform = 'translateX(-50%)';
    messageBox.style.padding = '1rem';
    messageBox.style.borderRadius = '8px';
    messageBox.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    messageBox.style.fontSize = '1rem';
    messageBox.style.color = '#fff';
    messageBox.style.zIndex = '1000';

    if (type === 'success') {
        messageBox.style.backgroundColor = '#4caf50';
    } else if (type === 'error') {
        messageBox.style.backgroundColor = '#f44336';
    } else {
        messageBox.style.backgroundColor = '#2196f3';
    }

    document.body.appendChild(messageBox);

    setTimeout(() => {
        messageBox.remove();
    }, 3000);
};

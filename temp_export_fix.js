// Bulletproof export function using direct download
function exportData(dataType) {
    const exportMessageContainer = document.getElementById('export-message-container');
    
    if (!exportMessageContainer) {
        console.error('Export message container not found');
        return;
    }
    
    // Use window.location.href for direct download - no JSON parsing issues
    showMessage(`Downloading ${dataType} export...`, 'info', exportMessageContainer);
    const url = `/api/export_data?type=${dataType}`;
    window.location.href = url;
    
    // Show success message after a delay
    setTimeout(() => {
        showMessage(`${dataType.replace('_', ' ')} export completed!`, 'success', exportMessageContainer);
    }, 2000);
}
document.addEventListener('DOMContentLoaded', function() {
    const newStoreBtn = document.getElementById('new-store-btn');
    const saveStoresBtn = document.getElementById('save-stores-btn');
    const storesTbody = document.getElementById('stores-tbody');
    const newStoreRowTemplate = document.getElementById('new-store-row-template');

    // Show new store row
    newStoreBtn.addEventListener('click', function() {
        const newRow = document.createElement('tr');
        newRow.className = 'new-store-row';
        newRow.innerHTML = `
            <td>
                <input type="text" class="form-control form-control-sm new-store-name" placeholder="Store Name">
            </td>
            <td>
                <input type="text" class="form-control form-control-sm new-store-address" placeholder="Address">
            </td>
            <td>
                <button type="button" class="btn btn-sm btn-secondary cancel-new-store-btn">Cancel</button>
            </td>
        `;
        storesTbody.insertBefore(newRow, storesTbody.firstChild);
        
        // Attach cancel handler to new row
        newRow.querySelector('.cancel-new-store-btn').addEventListener('click', function() {
            newRow.remove();
        });
        
        // Focus on name input
        newRow.querySelector('.new-store-name').focus();
    });

    // Delete store row
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-store-btn')) {
            const row = e.target.closest('tr');
            row.remove();
        }
    });

    // Save all stores
    saveStoresBtn.addEventListener('click', function() {
        const storesData = [];

        // Collect existing stores
        document.querySelectorAll('.store-row').forEach(row => {
            const storeId = row.getAttribute('data-store-id');
            const name = row.querySelector('.store-name').value.trim();
            const address = row.querySelector('.store-address').value.trim();

            if (name || address) {
                storesData.push({
                    id: storeId,
                    name: name,
                    address: address
                });
            }
        });

        // Collect new stores
        document.querySelectorAll('.new-store-row').forEach(row => {
            const name = row.querySelector('.new-store-name').value.trim();
            const address = row.querySelector('.new-store-address').value.trim();

            if (name || address) {
                storesData.push({
                    id: null,
                    name: name,
                    address: address
                });
            }
        });

        if (storesData.length === 0) {
            alert('No stores to save.');
            return;
        }

        console.log('Saving stores:', storesData);

        // API call to save stores
        fetch('/stores_save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stores: storesData
            })
        })
        .then(response => response.json())
        .then(data => {
            alert('Stores saved successfully!');
            // Reload the page to display updates
            window.location.reload();
        })
        .catch(error => {
            console.error('Error saving stores:', error);
            alert(`Failed to save stores: ${error.message}`);
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const tripCards = document.querySelectorAll('.trip-card');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    let currentIndex;

    // On load, the most recent (last in the list) "trip" should be visible
    // The most recent card in the list corresponds to the highest index.
    if (tripCards.length > 0) {
        currentIndex = tripCards.length - 1;

        // Function to show the current card and hide others
        function updateDisplay() {
            tripCards.forEach((card, index) => {
                // Hide all cards initially using Bootstrap's d-none class
                card.classList.add('d-none');
            });

            // Show the card at the current index
            tripCards[currentIndex].classList.remove('d-none');

            // Update button states
            prevBtn.disabled = currentIndex === 0;
            nextBtn.disabled = currentIndex === tripCards.length - 1;
        }

        // Initial display update
        updateDisplay();

        // On tapping the previous/next buttons should change the index
        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateDisplay();
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentIndex < tripCards.length - 1) {
                currentIndex++;
                updateDisplay();
            }
        });

    } else {
        // If there are no trips, disable navigation buttons
        prevBtn.disabled = true;
        nextBtn.disabled = true;
    }

    // === Logic for Store Dropdown Selection ===

    const storeNameSelects = document.querySelectorAll('.store-name-select');

    storeNameSelects.forEach(select => {
        select.addEventListener('change', function() {
            const card = this.closest('.card');
            const selectedOption = this.options[this.selectedIndex];

            // 1. Update Address
            const newAddress = selectedOption.getAttribute('data-address');
            const addressElement = card.querySelector('.current-trip-address');
            addressElement.textContent = newAddress;

            // 2. Show Save Button
            const saveButtonContainer = card.querySelector('.save-button-container');
            saveButtonContainer.classList.remove('d-none');
        });
    });

        // === Make summary editable and show Save button on change ===
        const summaryInputs = document.querySelectorAll('.trip-summary-input');
        summaryInputs.forEach(input => {
            input.addEventListener('input', function() {
                const card = this.closest('.card');
                const saveButtonContainer = card.querySelector('.save-button-container');
                if (this.value.trim().length > 0) {
                    saveButtonContainer.classList.remove('d-none');
                } else {
                    // If summary cleared and no other changes, keep save visible so user can intentionally clear summary
                    saveButtonContainer.classList.remove('d-none');
                }
            });
        });
});

// Add interactivity to the checklist buttons and item controls
function attachCheckHandler(button) {
    button.addEventListener('click', function() {
        // Toggle the style/state of the button
        this.classList.toggle('btn-outline-success');
        this.classList.toggle('btn-success');

        // Find the parent <tr> and visually cross out the row
        const row = this.closest('tr');
        row.classList.toggle('text-decoration-line-through');
        row.classList.toggle('table-success');
        // Show save when toggled
        const card = this.closest('.card');
        card.querySelector('.save-button-container').classList.remove('d-none');
    });
}

function attachDeleteHandler(button) {
    button.addEventListener('click', function() {
        const row = this.closest('tr');
        const card = this.closest('.card');
        row.remove();
        card.querySelector('.save-button-container').classList.remove('d-none');
    });
}

function attachItemInputHandlers(input) {
    input.addEventListener('input', function() {
        const card = this.closest('.card');
        card.querySelector('.save-button-container').classList.remove('d-none');
    });
}

// Attach handlers for existing controls on page load
document.querySelectorAll('.check-item-btn').forEach(attachCheckHandler);
document.querySelectorAll('.delete-item-btn').forEach(attachDeleteHandler);
document.querySelectorAll('.item-name-input').forEach(attachItemInputHandlers);
document.querySelectorAll('.item-quantity-input').forEach(attachItemInputHandlers);

// === Logic for Adding New Items and Showing Save Button ===
const newItemInputs = document.querySelectorAll('.new-item-name');

newItemInputs.forEach(input => {
    const card = input.closest('.card');
    const saveButtonContainer = card.querySelector('.save-button-container');
    const tableBody = card.querySelector('.trip-item-table tbody');
    const quantityInput = card.querySelector('.new-item-quantity');

    function addNewItem(name, quantity) {
        const newRow = document.createElement('tr');
        // leave data-item-id empty for new items (to be assigned by backend)

        const buttonCell = document.createElement('td');
        buttonCell.innerHTML = `<button type="button" class="btn btn-outline-success btn-sm check-item-btn">&#10003;</button>`;
        newRow.appendChild(buttonCell);

        const nameCell = document.createElement('td');
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.className = 'form-control item-name-input';
        nameInput.value = name;
        nameCell.appendChild(nameInput);
        newRow.appendChild(nameCell);

        const quantityCell = document.createElement('td');
        const qtyInput = document.createElement('input');
        qtyInput.type = 'number';
        qtyInput.className = 'form-control item-quantity-input';
        qtyInput.value = quantity;
        qtyInput.min = 1;
        quantityCell.appendChild(qtyInput);
        newRow.appendChild(quantityCell);

        const deleteCell = document.createElement('td');
        const delButton = document.createElement('button');
        delButton.type = 'button';
        delButton.className = 'btn btn-outline-danger btn-sm delete-item-btn';
        delButton.innerHTML = '&times;';
        deleteCell.appendChild(delButton);
        newRow.appendChild(deleteCell);

        // Insert before the new-item-row
        const newItemRow = card.querySelector('.new-item-row');
        tableBody.insertBefore(newRow, newItemRow);

        // Attach handlers
        attachCheckHandler(newRow.querySelector('.check-item-btn'));
        attachDeleteHandler(newRow.querySelector('.delete-item-btn'));
        attachItemInputHandlers(nameInput);
        attachItemInputHandlers(qtyInput);

        // Show save
        saveButtonContainer.classList.remove('d-none');
    }

    // show save when typing in the new item input
    input.addEventListener('input', function() {
        if (this.value.trim().length > 0) {
            saveButtonContainer.classList.remove('d-none');
        } else if (tableBody.querySelectorAll('tr').length === 1) {
            saveButtonContainer.classList.add('d-none');
        }
    });

    // Enter key adds the item
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.value.trim() !== "") {
            e.preventDefault();
            addNewItem(this.value.trim(), quantityInput.value || 1);
            this.value = '';
            quantityInput.value = 1;
        }
    });

    // Blur should also add the item (mobile tapping outside)
    input.addEventListener('blur', function(e) {
        const val = this.value.trim();
        if (val !== "") {
            // Delay slightly to allow potential Enter handler to run first
            setTimeout(() => {
                // If value still present (not cleared by enter handler), add it
                if (this.value.trim() === val) {
                    addNewItem(val, quantityInput.value || 1);
                    this.value = '';
                    quantityInput.value = 1;
                }
            }, 50);
        }
    });
});


// === Logic for Save Button Click (API POST preparation) ===
const saveButtons = document.querySelectorAll('.save-list-btn');

saveButtons.forEach(button => {
    button.addEventListener('click', function() {
        const card = this.closest('.card');
        const tripId = this.getAttribute('data-trip-id');

        const dateInput = card.querySelector('.trip-date-display');
        const tableRows = card.querySelectorAll('.trip-item-table tbody tr:not(.new-item-row)');
        
        // Capture current store and trip data
        const storeSelect = card.querySelector('.store-name-select');
        const tripName = storeSelect.value;
        const tripAddress = card.querySelector('.current-trip-address').textContent.trim();
        const tripSummary = card.querySelector('.trip-summary-input').value.trim();

        // Get the selected option element
        const selectedOption = storeSelect.options[storeSelect.selectedIndex];
        const storeId = selectedOption ? selectedOption.getAttribute('data-store-id') : null; // Capture the Store ID

        // Build the data structure to send to the API
        const listData = [];
        tableRows.forEach(row => {
            const listItemId = row.getAttribute('data-list-item-id');
            const itemId = row.getAttribute('data-item-id');
            const nameInput = row.querySelector('.item-name-input');
            const qtyInput = row.querySelector('.item-quantity-input');
            const nameVal = nameInput ? nameInput.value.trim() : '';
            const qtyVal = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

            // Only save the item if its name is present
            if (nameVal !== "") {
                listData.push({
                    id: listItemId,
                    itemId: itemId,
                    name: nameVal,
                    quantity: qtyVal
                });
            }
        });

        console.log(`Sending list for Trip ID: ${tripId}`, listData);

        // --- API Call ---
        fetch('/lists_save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Include any necessary CSRF tokens here
            },
            body: JSON.stringify({
                trip_id: tripId,
                summary: tripSummary,
                store_id: storeId,
                date: dateInput.value,
                store_name: tripName,
                store_address: tripAddress,
                items: listData,
            })
        })
        .then(response => response.json())
        .then(data => {
            alert('List saved successfully!');
            // Hide the save button after successful save
            card.querySelector('.save-button-container').classList.add('d-none');
        })
        .catch(error => {
            console.error('Error saving list:', error);
            alert(`Failed to save list because ${error.message}`);
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generate-btn');
    const saveBtn = document.getElementById('save-btn');
    const userPrompt = document.getElementById('user-prompt');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultsSection = document.getElementById('results-section');
    const mealsContainer = document.getElementById('meals-container');
    const itemsTableBody = document.getElementById('items-table-body');
    const tripDateInput = document.getElementById('trip-date');
    const tripSummaryInput = document.getElementById('trip-summary');

    // Set default trip date to today
    const today = new Date().toISOString().split('T')[0];
    tripDateInput.value = today;

    // Generate button click handler
    generateBtn.addEventListener('click', async function() {
        const prompt = userPrompt.value.trim();

        if (!prompt) {
            alert('Please enter a prompt describing your trip.');
            return;
        }

        // Show loading spinner
        loadingSpinner.classList.remove('d-none');
        generateBtn.disabled = true;

        try {
            const response = await fetch('/prompt_generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: prompt })
            });

            if (!response.ok) {
                const error = await response.json();
                alert('Failed to generate plan: ' + (error.error || 'Unknown error'));
                return;
            }

            const data = await response.json();
            console.log('Generated data:', data);

            // Display the results
            displayMeals(data.meals);
            displayItems(data.items);

            // Set trip summary from the prompt
            tripSummaryInput.value = prompt;

            // Pre-populate store dropdown if AI identified a store
            if (data.store_name && data.store_name !== 'Unknown Store') {
                selectStoreByName(data.store_name);
            }

            // Show results section
            resultsSection.classList.remove('d-none');

        } catch (error) {
            console.error('Error generating plan:', error);
            alert('Failed to generate plan: ' + error.message);
        } finally {
            // Hide loading spinner
            loadingSpinner.classList.add('d-none');
            generateBtn.disabled = false;
        }
    });

    // Display meals in cards
    function displayMeals(meals) {
        mealsContainer.innerHTML = '';

        meals.forEach((meal, index) => {
            const mealCard = document.createElement('div');
            mealCard.className = 'card meal-card w-100 mb-3 shadow-lg border-0';
            mealCard.innerHTML = `
                <div class="card-body">
                    <div class="row g-2 mb-3">
                        <div class="col-md-6">
                            <input type="date" class="form-control meal-date" value="${meal.date}" data-meal-index="${index}">
                        </div>
                        <div class="col-md-6">
                            <select class="form-select meal-type" data-meal-index="${index}">
                                <option value="Breakfast" ${meal.type === 'Breakfast' ? 'selected' : ''}>Breakfast</option>
                                <option value="Hameikatako" ${meal.type === 'Hameikatako' ? 'selected' : ''}>Hameikatako</option>
                                <option value="Lunch" ${meal.type === 'Lunch' ? 'selected' : ''}>Lunch</option>
                                <option value="Dinner" ${meal.type === 'Dinner' ? 'selected' : ''}>Dinner</option>
                            </select>
                        </div>
                    </div>
                    <div class="mb-3">
                        <textarea class="form-control meal-summary" data-meal-index="${index}">${meal.summary}</textarea>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger delete-meal-btn" data-meal-index="${index}">Delete</button>
                </div>
            `;
            mealsContainer.appendChild(mealCard);
        });

        // Add delete handlers
        document.querySelectorAll('.delete-meal-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const mealCard = this.closest('.meal-card');
                mealCard.remove();
            });
        });
    }

    // Display items in table
    function displayItems(items) {
        itemsTableBody.innerHTML = '';

        items.forEach((item, index) => {
            const row = document.createElement('tr');
            row.setAttribute('data-item-index', index);
            row.innerHTML = `
                <td>
                    <button type="button" class="btn btn-outline-success btn-sm check-item-btn">&#10003;</button>
                </td>
                <td>
                    <input type="text" class="form-control item-name-input" value="${item.name}">
                </td>
                <td>
                    <input type="number" class="form-control item-quantity-input" value="${item.quantity}" min="1">
                </td>
                <td>
                    <button type="button" class="btn btn-outline-danger btn-sm delete-item-btn">&times;</button>
                </td>
            `;
            itemsTableBody.appendChild(row);
        });

        // Add row for new items
        const newItemRow = document.createElement('tr');
        newItemRow.className = 'new-item-row';
        newItemRow.innerHTML = `
            <td></td>
            <td><input type="text" class="form-control new-item-name" placeholder="New Item"></td>
            <td><input type="number" class="form-control new-item-quantity" value="1" min="1"></td>
            <td></td>
        `;
        itemsTableBody.appendChild(newItemRow);

        // Add delete handlers for items
        document.querySelectorAll('.delete-item-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const row = this.closest('tr');
                row.remove();
            });
        });

        // Add check handlers for items (strikethrough)
        document.querySelectorAll('.check-item-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const row = this.closest('tr');
                row.classList.toggle('text-decoration-line-through');
            });
        });

        // Handle new item entry
        const newItemName = newItemRow.querySelector('.new-item-name');
        newItemName.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addNewItem();
            }
        });
    }

    // Select store by name in the dropdown
    function selectStoreByName(storeName) {
        const storeSelect = document.getElementById('store-select');
        const options = storeSelect.options;

        // Find the option that matches the store name (case-insensitive partial match)
        for (let i = 0; i < options.length; i++) {
            const optionValue = options[i].value.toLowerCase();
            const searchName = storeName.toLowerCase();

            // Check for exact match or if the store name contains the search term
            if (optionValue === searchName || optionValue.includes(searchName) || searchName.includes(optionValue)) {
                storeSelect.selectedIndex = i;
                console.log('Pre-selected store:', options[i].value);
                break;
            }
        }
    }

    // Add a new item row
    function addNewItem() {
        const newItemName = document.querySelector('.new-item-name');
        const newItemQuantity = document.querySelector('.new-item-quantity');
        const name = newItemName.value.trim();
        const quantity = parseFloat(newItemQuantity.value);

        if (!name) {
            return;
        }

        // Get current items
        const currentRows = itemsTableBody.querySelectorAll('tr:not(.new-item-row)');
        const newIndex = currentRows.length;

        // Create new row
        const row = document.createElement('tr');
        row.setAttribute('data-item-index', newIndex);
        row.innerHTML = `
            <td>
                <button type="button" class="btn btn-outline-success btn-sm check-item-btn">&#10003;</button>
            </td>
            <td>
                <input type="text" class="form-control item-name-input" value="${name}">
            </td>
            <td>
                <input type="number" class="form-control item-quantity-input" value="${quantity}" min="1">
            </td>
            <td>
                <button type="button" class="btn btn-outline-danger btn-sm delete-item-btn">&times;</button>
            </td>
        `;

        // Insert before the new-item-row
        const newItemRow = itemsTableBody.querySelector('.new-item-row');
        itemsTableBody.insertBefore(row, newItemRow);

        // Clear the new item inputs
        newItemName.value = '';
        newItemQuantity.value = '1';

        // Add event handlers
        row.querySelector('.delete-item-btn').addEventListener('click', function() {
            row.remove();
        });

        row.querySelector('.check-item-btn').addEventListener('click', function() {
            row.classList.toggle('text-decoration-line-through');
        });
    }

    // Save button click handler
    saveBtn.addEventListener('click', async function() {
        // Collect meals data
        const mealsData = [];
        document.querySelectorAll('.meal-card').forEach(card => {
            const date = card.querySelector('.meal-date').value;
            const type = card.querySelector('.meal-type').value;
            const summary = card.querySelector('.meal-summary').value.trim();

            if (date && type && summary) {
                mealsData.push({
                    id: null, // New meal, no ID yet
                    date: date,
                    type: type,
                    summary: summary
                });
            }
        });

        // Collect items data
        const itemsData = [];
        document.querySelectorAll('#items-table-body tr:not(.new-item-row)').forEach(row => {
            const name = row.querySelector('.item-name-input').value.trim();
            const quantity = parseFloat(row.querySelector('.item-quantity-input').value);

            if (name) {
                itemsData.push({
                    id: null, // New item, no row ID yet
                    itemId: null, // Will be determined by backend
                    name: name,
                    quantity: quantity
                });
            }
        });

        if (mealsData.length === 0 && itemsData.length === 0) {
            alert('No data to save.');
            return;
        }

        const tripDate = tripDateInput.value;
        const tripSummary = tripSummaryInput.value.trim();

        // Get store information
        const storeSelect = document.getElementById('store-select');
        const selectedOption = storeSelect.options[storeSelect.selectedIndex];
        const storeId = selectedOption ? selectedOption.getAttribute('data-store-id') : null;
        const storeName = selectedOption ? selectedOption.value : null;
        const storeAddress = selectedOption ? selectedOption.getAttribute('data-address') : null;

        console.log('Saving data:', {
            meals: mealsData,
            items: itemsData,
            date: tripDate,
            summary: tripSummary,
            store_id: storeId,
            store_name: storeName,
            store_address: storeAddress
        });

        try {
            const response = await fetch('/prompt_save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    meals: mealsData,
                    items: itemsData,
                    date: tripDate,
                    summary: tripSummary,
                    store_id: storeId,
                    store_name: storeName,
                    store_address: storeAddress
                })
            });

            if (!response.ok) {
                const error = await response.json();
                alert('Failed to save data: ' + (error.error || 'Unknown error'));
                return;
            }

            alert('Data saved successfully!');
            // Redirect to home page
            window.location.href = '/';

        } catch (error) {
            console.error('Error saving data:', error);
            alert('Failed to save data: ' + error.message);
        }
    });
});

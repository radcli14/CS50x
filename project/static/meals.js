document.addEventListener('DOMContentLoaded', function() {
    const newMealBtn = document.getElementById('new-meal-btn');
    const saveMealsBtn = document.getElementById('save-meals-btn');
    const newMealCard = document.querySelector('.new-meal-card');
    const cancelNewMealBtn = document.querySelector('.cancel-new-meal-btn');
    const mealsContainer = document.getElementById('meals-container');

    // Show new meal card at the top
    newMealBtn.addEventListener('click', function() {
        newMealCard.classList.remove('d-none');
        // Move card to top of container
        mealsContainer.insertBefore(newMealCard, mealsContainer.firstChild);
        // Set default date to today
        const today = new Date().toISOString().split('T')[0];
        document.querySelector('.new-meal-date').value = today;
        document.querySelector('.new-meal-type').value = 'Breakfast';
        document.querySelector('.new-meal-summary').value = '';
    });

    // Cancel new meal entry
    cancelNewMealBtn.addEventListener('click', function() {
        newMealCard.classList.add('d-none');
        // Clear the form
        document.querySelector('.new-meal-date').value = '';
        document.querySelector('.new-meal-type').value = 'Breakfast';
        document.querySelector('.new-meal-summary').value = '';
    });

    // Delete meal
    document.querySelectorAll('.delete-meal-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const mealCard = this.closest('.meal-card');
            mealCard.remove();
        });
    });

    // Save all meals
    saveMealsBtn.addEventListener('click', function() {
        const mealsData = [];

        // Collect existing meals
        document.querySelectorAll('.meal-card').forEach(card => {
            const mealId = card.querySelector('.meal-date').getAttribute('data-meal-id');
            const date = card.querySelector('.meal-date').value;
            const type = card.querySelector('.meal-type').value;
            const summary = card.querySelector('.meal-summary').value.trim();

            mealsData.push({
                id: mealId,
                date: date,
                type: type,
                summary: summary
            });
        });

        // Collect new meal if card is visible
        if (!newMealCard.classList.contains('d-none')) {
            const date = document.querySelector('.new-meal-date').value;
            const type = document.querySelector('.new-meal-type').value;
            const summary = document.querySelector('.new-meal-summary').value.trim();

            if (date && type && summary) {
                mealsData.push({
                    id: null,
                    date: date,
                    type: type,
                    summary: summary
                });
            } else {
                alert('Please fill in all fields for the new meal.');
                return;
            }
        }

        if (mealsData.length === 0) {
            alert('No meals to save.');
            return;
        }

        console.log('Saving meals:', mealsData);

        // API call to save meals
        fetch('/meals_save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                meals: mealsData
            })
        })
        .then(response => response.json())
        .then(data => {
            alert('Meals saved successfully!');
            // Reload the page to display the new meal
            window.location.reload();
        })
        .catch(error => {
            console.error('Error saving meals:', error);
            alert(`Failed to save meals: ${error.message}`);
        });
    });
});

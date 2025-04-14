const searchBar = document.getElementById('search-bar');
const searchForm = document.getElementById('search-form');
const searchButton = document.getElementById('search-button');

// Keep the previous search button functionality
searchForm.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevent default form submission

    const query = searchBar.value.trim();
    
    if (query === '') {
        alert('Please enter a search query');
    } else {
        fetch(`http://127.0.0.1:5000/search?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('An error occurred while fetching the search results: ' + data.error);
                } else {
                    window.location.href = `results-html,css,js.html?query=${encodeURIComponent(query)}`;
                }
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                alert('An error occurred while fetching the search results.');
            });
    }
});

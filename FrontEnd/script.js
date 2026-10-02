const UPDATE_API_URL = 'https://czrng483o3.execute-api.us-east-1.amazonaws.com/update_api/update_api';
const SEARCH_API_URL = 'https://fmnflo4gma.execute-api.us-east-1.amazonaws.com/search_api/search_api';

const availableMoviesElement = document.getElementById('available-movies');
const movieInput = document.getElementById('movie-id-input');
const searchButton = document.getElementById('search-btn');
const tableBody = document.getElementById('table-body');
const searchStatus = document.getElementById('search-status');
const currentYear = document.getElementById('current-year');

document.addEventListener('DOMContentLoaded', () => {
    fetchAvailableMovies();

    if (currentYear) {
        currentYear.textContent = new Date().getFullYear();
    }
});

searchButton.addEventListener('click', searchMovie);

movieInput.addEventListener('keydown', event => {
    if (event.key === 'Enter') {
        searchMovie();
    }
});

async function fetchAvailableMovies() {
    if (UPDATE_API_URL === 'UPDATE API GOES HERE') {
        availableMoviesElement.textContent =
            'Connect the AfroCinemax Update API to display live movie availability.';
        return;
    }

    try {
        availableMoviesElement.textContent = 'Loading available movies...';

        const response = await fetch(UPDATE_API_URL);

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();

        if (!Array.isArray(data) || data.length === 0) {
            availableMoviesElement.textContent =
                'No movies are currently available.';
            return;
        }

        availableMoviesElement.innerHTML = '';

        data.forEach(movie => {
            const movieBadge = document.createElement('span');
            movieBadge.className = 'movie-badge';
            movieBadge.textContent = movie;
            availableMoviesElement.appendChild(movieBadge);
        });
    } catch (error) {
        console.error('Error fetching available movies:', error);

        availableMoviesElement.textContent =
            'Unable to load movie availability right now.';
    }
}

async function searchMovie() {
    const movieName = movieInput.value.trim();

    if (!movieName) {
        setSearchStatus('Please enter a movie title first.', 'warning');
        movieInput.focus();
        return;
    }

    if (SEARCH_API_URL === 'SEARCH API GOES HERE') {
        setSearchStatus(
            'Connect the AfroCinemax Search API before searching for movies.',
            'warning'
        );
        return;
    }

    setLoadingState(true);

    try {
        const query = encodeURIComponent(movieName);
        const response = await fetch(
            `${SEARCH_API_URL}?movieName=${query}`
        );

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();

        tableBody.innerHTML = '';

        if (Array.isArray(data) && data.length > 0) {
            data.forEach(movie => {
                tableBody.appendChild(createMovieRow(movie));
            });

            setSearchStatus(
                `${data.length} result${data.length === 1 ? '' : 's'} found for "${movieName}".`,
                'success'
            );
        } else {
            setSearchStatus(
                `No movies found for "${movieName}". Try another title.`,
                'neutral'
            );
        }
    } catch (error) {
        console.error('Error fetching movie data:', error);

        tableBody.innerHTML = '';

        setSearchStatus(
            'We could not retrieve movie information. Please try again later.',
            'error'
        );
    } finally {
        setLoadingState(false);
    }
}

function createMovieRow(movie) {
    const row = document.createElement('tr');

    const values = [
        movie.movies ?? 'Unknown',
        movie.year ?? 'N/A',
        movie.time ?? 'N/A',
        movie.rating ?? 'N/A',
        movie.description ?? 'No description available.'
    ];

    values.forEach((value, index) => {
        const cell = document.createElement('td');

        if (index === 0) {
            cell.className = 'movie-title-cell';
        }

        if (index === 3) {
            cell.className = 'rating-cell';
            cell.textContent = `★ ${value}`;
        } else {
            cell.textContent = value;
        }

        row.appendChild(cell);
    });

    return row;
}

function setSearchStatus(message, type = 'neutral') {
    searchStatus.textContent = message;
    searchStatus.className = `search-status ${type}`;
}

function setLoadingState(isLoading) {
    searchButton.disabled = isLoading;

    if (isLoading) {
        searchButton.textContent = 'Searching...';
        setSearchStatus('Searching AfroCinemax...', 'loading');
    } else {
        searchButton.textContent = 'Search Movie';
    }
}
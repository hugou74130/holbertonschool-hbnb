/*
  HBnB - Part 4
  Client-side scripts
*/

const API_URL = 'http://127.0.0.1:5000';

document.addEventListener('DOMContentLoaded', () => {

    /* ── Login page ─────────────────────────────────────────────────── */
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            await loginUser(email, password);
        });
    }

    /* ── Index page ─────────────────────────────────────────────────── */
    const priceFilter = document.getElementById('price-filter');
    if (priceFilter) {
        checkAuthentication();

        priceFilter.addEventListener('change', (event) => {
            const selected = event.target.value;
            document.querySelectorAll('.place-card').forEach((card) => {
                if (selected === 'all') {
                    card.style.display = 'block';
                } else {
                    const price = parseFloat(card.dataset.price);
                    card.style.display = price <= parseFloat(selected) ? 'block' : 'none';
                }
            });
        });
    }

    /* ── Place details page ─────────────────────────────────────────── */
    const placeDetails = document.getElementById('place-details');
    if (placeDetails) {
        const placeId = getPlaceIdFromURL();
        if (placeId) {
            checkAuthenticationPlace(placeId);
        }
    }

    /* ── Add review page (place.html inline form) ───────────────────── */
    const placeReviewForm = document.querySelector('#place-details ~ #add-review #review-form');
    if (placeReviewForm) {
        placeReviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const token = getCookie('token');
            if (!token) {
                alert('Please login to submit a review');
                return;
            }
            const placeId = getPlaceIdFromURL();
            const comment = document.getElementById('review').value;
            const rating = parseInt(document.getElementById('rating').value);
            await submitReview(token, placeId, comment, rating);
        });
    }

    /* ── Add review page (standalone) ───────────────────────────────── */
    const reviewForm = document.getElementById('review-form');
    if (reviewForm && !document.getElementById('place-details')) {
        const token = checkAuthenticationReview();
        const placeId = getPlaceIdFromURL();

        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const comment = document.getElementById('review').value;
            const rating = parseInt(document.getElementById('rating').value);
            await submitReview(token, placeId, comment, rating);
        });
    }
});

/* ══ Helpers ════════════════════════════════════════════════════════════ */

function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return value;
    }
    return null;
}

function getPlaceIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

function getTokenPayload(token) {
    try {
        const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(base64));
    } catch (e) {
        return null;
    }
}

/* ══ Authentication ══════════════════════════════════════════════════════ */

/* Index page: show/hide login link + fetch places */
function checkAuthentication() {
    const token = getCookie('token');
    const loginLink = document.getElementById('login-link');
    const userInfo = document.getElementById('user-info');

    if (!token) {
        if (loginLink) loginLink.style.display = 'block';
        if (userInfo) userInfo.style.display = 'none';
    } else {
        if (loginLink) loginLink.style.display = 'none';
        if (userInfo) userInfo.style.display = 'inline';
        
        // Fetch current user info
        fetchCurrentUser(token);
        fetchPlaces(token);
    }
    
    // Logout functionality
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
            window.location.href = 'login.html';
        });
    }
}

function checkAuthenticationPlace(placeId) {
    const token = getCookie('token');
    const addReviewSection = document.getElementById('add-review');
    const loginLink = document.getElementById('login-link');
    const userInfo = document.getElementById('user-info');

    if (!token) {
        if (addReviewSection) addReviewSection.style.display = 'none';
        if (loginLink) loginLink.style.display = 'block';
        if (userInfo) userInfo.style.display = 'none';
    } else {
        if (addReviewSection) addReviewSection.style.display = 'block';
        if (loginLink) loginLink.style.display = 'none';
        if (userInfo) userInfo.style.display = 'inline';
        
        // Fetch current user info
        fetchCurrentUser(token);
    }

    fetchPlaceDetails(token, placeId);
    
    // Logout functionality
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
            window.location.href = 'login.html';
        });
    }
}

function checkAuthenticationReview() {
    const token = getCookie('token');
    if (!token) {
        window.location.href = 'index.html';
        return null;
    }
    return token;
}

/* ══ Login ══════════════════════════════════════════════════════════════ */

async function fetchCurrentUser(token) {
    const response = await fetch(`${API_URL}/api/v1/users/me`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    });

    if (response.ok) {
        const user = await response.json();
        const userNameElement = document.getElementById('user-name');
        if (userNameElement) {
            userNameElement.textContent = `👋 ${user.first_name}`;
        }
    }
}

async function loginUser(email, password) {
    const response = await fetch(`${API_URL}/api/v1/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    if (response.ok) {
        const data = await response.json();
        document.cookie = `token=${data.access_token}; path=/`;
        window.location.href = 'index.html';
    } else {
        alert('Login failed: ' + response.statusText);
    }
}

/* ══ Places (index) ═════════════════════════════════════════════════════ */

async function fetchPlaces(token) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_URL}/api/v1/places/`, {
        method: 'GET',
        headers
    });

    if (response.ok) {
        const places = await response.json();
        displayPlaces(places);
    } else {
        console.error('Failed to fetch places:', response.statusText);
    }
}

function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = '';

    places.forEach((place) => {
        const card = document.createElement('div');
        card.classList.add('place-card');
        card.dataset.price = place.price ?? 0;

        card.innerHTML = `
            <h2>${place.title}</h2>
            <p><strong>Price per night:</strong> $${place.price ?? 'N/A'}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;

        placesList.appendChild(card);
    });
}

/* ══ Place details ══════════════════════════════════════════════════════ */

async function fetchPlaceDetails(token, placeId) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_URL}/api/v1/places/${placeId}`, {
        method: 'GET',
        headers
    });

    if (response.ok) {
        const place = await response.json();
        displayPlaceDetails(place);
        await fetchReviews(token, placeId);
    } else {
        console.error('Failed to fetch place details:', response.statusText);
    }
}

function displayPlaceDetails(place) {
    const placeInfo = document.querySelector('#place-details .place-info');
    placeInfo.innerHTML = '';

    const amenitiesList = place.amenities && place.amenities.length
        ? place.amenities.map(a => `<li>${a.name}</li>`).join('')
        : '<li>No amenities listed</li>';

    placeInfo.innerHTML = `
        <h1>${place.title}</h1>
        <p><strong>Host:</strong> ${place.owner.first_name} ${place.owner.last_name}</p>
        <p><strong>Price per night:</strong> $${place.price}</p>
        <p><strong>Description:</strong> ${place.description || 'No description available'}</p>
        <div class="amenities">
            <h3>Amenities</h3>
            <ul>${amenitiesList}</ul>
        </div>
    `;
}

async function fetchReviews(token, placeId) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_URL}/api/v1/reviews/places/${placeId}/reviews`, {
        method: 'GET',
        headers
    });

    if (response.ok) {
        const reviews = await response.json();
        displayReviews(reviews);
    } else {
        console.error('Failed to fetch reviews:', response.statusText);
    }
}

function displayReviews(reviews) {
    const reviewsSection = document.getElementById('reviews');
    const heading = reviewsSection.querySelector('h3');
    reviewsSection.innerHTML = '';
    if (heading) reviewsSection.appendChild(heading);

    if (!reviews.length) {
        const empty = document.createElement('p');
        empty.textContent = 'No reviews yet.';
        reviewsSection.appendChild(empty);
        return;
    }

    reviews.forEach((review) => {
        const card = document.createElement('div');
        card.classList.add('review-card');
        card.innerHTML = `
            <p><strong>Rating:</strong> ${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</p>
            <p>${review.comment}</p>
        `;
        reviewsSection.appendChild(card);
    });
}

/* ══ Add review ═════════════════════════════════════════════════════════ */

async function submitReview(token, placeId, comment, rating) {
    const payload = getTokenPayload(token);
    const userId = payload ? (payload.sub || payload.id) : null;

    const response = await fetch(`${API_URL}/api/v1/reviews/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            comment,
            rating,
            place_id: placeId,
            user_id: userId
        })
    });

    handleResponse(response);
}

async function handleResponse(response) {
    if (response.ok) {
        alert('Review submitted successfully!');
        const reviewForm = document.getElementById('review-form');
        if (reviewForm) reviewForm.reset();
        
        // Refresh reviews if on place details page
        if (document.getElementById('place-details')) {
            const token = getCookie('token');
            const placeId = getPlaceIdFromURL();
            await fetchReviews(token, placeId);
        }
    } else {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.error || errorData.message || response.statusText;
        alert('Failed to submit review: ' + errorMessage);
    }
}

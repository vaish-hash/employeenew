    // --- service-worker.js ---
    // This file acts as a proxy between the web app and the network.
    // It enables offline capabilities and caching strategies for the PWA.

    const CACHE_NAME = 'mnc-worker-app-cache-v1'; // Cache version. Increment this to force updates.
    const urlsToCache = [
      '/', // Cache the root path (index.html will be served)
      '/index', // Ensure the main entry point is cached
      '/login', // Cache the login page
      '/static/style.css',
      '/static/script.js',
      '/static/manifest.json',
      '/static/icons/icon-192x192.png', // Ensure icons are cached
      '/static/icons/icon-512x512.png', // Ensure icons are cached
      // Add other essential static assets and HTML pages here
      '/actual_hours',
      '/assign_employee', // Assuming this is the route for assign_employee.html
      '/members',
      '/projects',
      '/workload_current',
      '/monthly_workload',
      '/export_data',
      '/import_data',
      '/app_stopped' // Crucial: Cache the app_stopped page for offline display
    ];

    // --- Install Event ---
    // This event is fired when the service worker is first installed.
    // It's used to populate the initial cache with essential assets.
    self.addEventListener('install', event => {
      event.waitUntil(
        caches.open(CACHE_NAME)
          .then(cache => {
            console.log('Service Worker: Caching essential app shell assets');
            return cache.addAll(urlsToCache); // Add all specified URLs to the cache
          })
          .catch(error => {
            console.error('Service Worker: Failed to cache during install:', error);
          })
      );
    });

    // --- Activate Event ---
    // This event is fired when the service worker is activated.
    // It's typically used to clean up old caches.
    self.addEventListener('activate', event => {
      event.waitUntil(
        caches.keys().then(cacheNames => {
          return Promise.all(
            cacheNames.map(cacheName => {
              if (cacheName !== CACHE_NAME) {
                console.log('Service Worker: Deleting old cache:', cacheName);
                return caches.delete(cacheName); // Delete old caches
              }
            })
          );
        })
      );
    });

    // --- Fetch Event ---
    // This event is fired for every network request made by the web app.
    // It allows the service worker to intercept requests and serve from cache if available.
    self.addEventListener('fetch', event => {
      event.respondWith(
        caches.match(event.request) // Try to find the request in the cache first
          .then(response => {
            // If the request is in the cache, return the cached response
            if (response) {
              return response;
            }
            // If not in cache, fetch from the network
            return fetch(event.request).then(
              function(response) {
                // Check if we received a valid response
                if(!response || response.status !== 200 || response.type !== 'basic') {
                  return response;
                }

                // IMPORTANT: Clone the response. A response is a stream
                // and can only be consumed once. We must clone it so that
                // both the browser and the cache can consume it.
                var responseToCache = response.clone();

                caches.open(CACHE_NAME)
                  .then(function(cache) {
                    cache.put(event.request, responseToCache); // Cache the new response
                  });

                return response;
              }
            ).catch(error => {
                // This catch block handles network errors (e.g., no internet connection)
                console.error('Service Worker: Fetch failed:', event.request.url, error);
                // If a network request fails, try to serve a fallback page
                // This is especially important for the 'offline' experience.
                // For our specific "stop date" bug, if the server actively sends
                // a redirect to /app_stopped, the browser will follow it.
                // If there's a complete network failure, this might show a generic offline page.
                // For now, we'll just return a generic error or a cached app_stopped page.
                if (event.request.mode === 'navigate') { // If it's a navigation request (e.g., user clicked a link or typed URL)
                    return caches.match('/app_stopped'); // Try to serve the cached app_stopped page
                }
                // For other types of requests (e.g., API calls), just let the error propagate
                return new Response('<h1>Offline or App Unavailable</h1><p>The application is currently not available or you are offline. Please check your internet connection or try again later.</p>', {
                    headers: { 'Content-Type': 'text/html' }
                });
            });
          })
      );
    });
    
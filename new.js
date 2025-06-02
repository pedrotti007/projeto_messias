    const response = await fetch("{{ url_for('tirar_duvidas_route') }}", { /* ... */ });

    document.addEventListener('DOMContentLoaded', function() {
    const loadingOverlay = document.getElementById('loading-overlay');

    const navigationLinks = document.querySelectorAll('a:not([href^="#"]):not([target="_blank"]):not([href*="javascript:void(0)"])');

    const loaderShownSessionKey = 'appLoaderHasBeenShownThisSession';

    navigationLinks.forEach(link => {
        link.addEventListener('click', function(event) {

            if (!sessionStorage.getItem(loaderShownSessionKey)) {
                if (this.href && (this.protocol === 'http:' || this.protocol === 'https:')) {

                    if (loadingOverlay) {
                        loadingOverlay.style.display = 'flex';
                    }
                    sessionStorage.setItem(loaderShownSessionKey, 'true');
                    setTimeout(() => {
                        if (loadingOverlay) {
                            loadingOverlay.style.display = 'none';
                        }
                    }, 1800);
                }
            }
        });
    });
    window.addEventListener('pageshow', function(event) {
        if (event.persisted && sessionStorage.getItem(loaderShownSessionKey)) {
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
        }
    });
});
/**
 * Sistema di fallback per le copertine dei giochi.
 * 
 * Strategia:
 * 1. Prova a caricare l'immagine dal src (se disponibile)
 * 2. Se l'immagine non carica o src è vuoto, chiama /api/game-cover
 * 3. CheapShark cercherà una copertina da vari store
 * 4. Se tutto fallisce, mostra il placeholder emoji
 */

(() => {
    // Mostra il placeholder emoji quando la copertina non carica
    const showPlaceholder = (container) => {
        const img = container.querySelector('.game-cover-image');
        const placeholder = container.querySelector('.game-image-placeholder');
        
        if (img) {
            img.style.display = 'none';
        }
        if (placeholder) {
            placeholder.removeAttribute('hidden');
        }
    };

    // Nasconde il placeholder e mostra l'immagine
    const showImage = (img) => {
        img.style.display = '';
        const container = img.closest('[data-cover-container]');
        if (container) {
            const placeholder = container.querySelector('.game-image-placeholder');
            if (placeholder) {
                placeholder.setAttribute('hidden', '');
            }
        }
    };

    // Tenta di caricare una copertina fallback da CheapShark
    const loadFallback = async (img, gameTitle) => {
        if (!gameTitle || gameTitle.length > 200) {
            showPlaceholder(img.closest('[data-cover-container]'));
            return;
        }

        try {
            const response = await fetch(
                `/api/game-cover?title=${encodeURIComponent(gameTitle)}`,
                { headers: { Accept: 'application/json' } }
            );

            if (!response.ok) {
                console.warn(`Cover lookup failed for "${gameTitle}": ${response.status}`);
                showPlaceholder(img.closest('[data-cover-container]'));
                return;
            }

            const { cover_url: coverUrl } = await response.json();
            
            if (!coverUrl) {
                console.warn(`No cover URL found for "${gameTitle}"`);
                showPlaceholder(img.closest('[data-cover-container]'));
                return;
            }

            // Imposta la nuova sorgente e prepara i listener
            img.onload = () => showImage(img);
            img.onerror = () => {
                console.warn(`Failed to load cover from fallback URL for "${gameTitle}"`);
                showPlaceholder(img.closest('[data-cover-container]'));
            };
            
            // Trigger del caricamento
            img.src = coverUrl;
        } catch (error) {
            console.error(`Error loading cover for "${gameTitle}":`, error);
            showPlaceholder(img.closest('[data-cover-container]'));
        }
    };

    // Inizializza tutte le immagini sulla pagina
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('[data-cover-fallback]').forEach((img) => {
            const gameTitle = img.dataset.gameTitle;
            const container = img.closest('[data-cover-container]');

            if (!container) {
                console.warn('Image without data-cover-container:', img);
                return;
            }

            // Se l'immagine ha già un src, tenta di caricarla
            if (img.src) {
                img.onload = () => showImage(img);
                img.onerror = () => {
                    console.warn(`Failed to load primary cover for "${gameTitle}", trying fallback...`);
                    loadFallback(img, gameTitle);
                };
            } else {
                // Nessun src disponibile, vai diretto al fallback
                loadFallback(img, gameTitle);
            }
        });
    });

    // Fallback per il caso in cui DOMContentLoaded sia già passato
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            // L'evento è gestito sopra
        });
    } else {
        // Pagina già caricata, esegui immediatamente
        document.querySelectorAll('[data-cover-fallback]').forEach((img) => {
            const gameTitle = img.dataset.gameTitle;
            const container = img.closest('[data-cover-container]');

            if (!container) return;

            if (img.src) {
                img.onload = () => showImage(img);
                img.onerror = () => {
                    console.warn(`Failed to load primary cover for "${gameTitle}", trying fallback...`);
                    loadFallback(img, gameTitle);
                };
            } else {
                loadFallback(img, gameTitle);
            }
        });
    }
})();
(() => {
    const showPlaceholder = (image) => {
        image.hidden = true;
        image.closest('[data-cover-container]')
            ?.querySelector('.game-image-placeholder')
            ?.removeAttribute('hidden');
    };

    const loadFallback = async (image) => {
        if (image.dataset.fallbackAttempted === 'true') return;
        image.dataset.fallbackAttempted = 'true';

        const title = image.dataset.gameTitle;
        if (!title) {
            showPlaceholder(image);
            return;
        }

        try {
            const response = await fetch(`/api/game-cover?title=${encodeURIComponent(title)}`, {
                headers: { Accept: 'application/json' },
            });
            if (!response.ok) throw new Error(`Cover lookup failed: ${response.status}`);

            const { cover_url: coverUrl } = await response.json();
            if (!coverUrl) throw new Error('Cover URL missing');

            image.addEventListener('error', () => showPlaceholder(image), { once: true });
            image.addEventListener('load', () => {
                image.hidden = false;
                image.closest('[data-cover-container]')
                    ?.querySelector('.game-image-placeholder')
                    ?.setAttribute('hidden', '');
            }, { once: true });
            image.src = coverUrl;
        } catch (_error) {
            showPlaceholder(image);
        }
    };

    document.querySelectorAll('[data-cover-fallback]').forEach((image) => {
        image.addEventListener('error', () => loadFallback(image), { once: true });
        if (!image.getAttribute('src')) loadFallback(image);
    });
})();

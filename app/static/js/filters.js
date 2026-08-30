document.addEventListener('DOMContentLoaded', () => {
    const perPageSelect = document.querySelector('[data-per-page-select]');

    if (!perPageSelect) {
        return;
    }

    perPageSelect.addEventListener('change', (event) => {
        const params = new URLSearchParams(window.location.search);
        params.set('per_page', event.target.value);
        params.set('page', '1');
        window.location.search = params.toString();
    });
});

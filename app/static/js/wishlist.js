const WISHLIST_STORAGE_KEY = 'game-deal-scraper:wishlist';

function readWishlist() {
    try {
        const value = JSON.parse(localStorage.getItem(WISHLIST_STORAGE_KEY) || '[]');
        return Array.isArray(value) ? value.filter((game) => game && game.id && game.title) : [];
    } catch (error) {
        console.warn('Impossibile leggere la wishlist salvata.', error);
        return [];
    }
}

function writeWishlist(games) {
    try {
        localStorage.setItem(WISHLIST_STORAGE_KEY, JSON.stringify(games));
        return true;
    } catch (error) {
        console.warn('Impossibile salvare la wishlist.', error);
        return false;
    }
}

function updateWishlistCount(games = readWishlist()) {
    document.querySelectorAll('[data-wishlist-count]').forEach((counter) => {
        counter.textContent = games.length;
        counter.setAttribute('aria-label', `${games.length} giochi salvati`);
    });
}

function setButtonState(button, isSaved) {
    const title = button.dataset.gameTitle;
    button.classList.toggle('is-saved', isSaved);
    button.setAttribute('aria-pressed', String(isSaved));
    button.setAttribute('aria-label', `${isSaved ? 'Rimuovi' : 'Aggiungi'} ${title} ${isSaved ? 'dalla' : 'alla'} wishlist`);
    button.title = isSaved ? 'Rimuovi dalla wishlist' : 'Aggiungi alla wishlist';
    button.querySelector('span').textContent = isSaved ? '♥' : '♡';
}

function initialiseWishlistButtons() {
    const buttons = document.querySelectorAll('[data-wishlist-button]');
    let games = readWishlist();

    buttons.forEach((button) => {
        setButtonState(button, games.some((game) => game.id === button.dataset.gameId));
        button.addEventListener('click', () => {
            games = readWishlist();
            const index = games.findIndex((game) => game.id === button.dataset.gameId);

            if (index >= 0) {
                games.splice(index, 1);
            } else {
                games.push({
                    id: button.dataset.gameId,
                    title: button.dataset.gameTitle,
                    image: button.dataset.gameImage,
                    price: button.dataset.gamePrice,
                    shop: button.dataset.gameShop,
                    type: button.dataset.gameType,
                });
            }

            if (writeWishlist(games)) {
                setButtonState(button, index < 0);
                updateWishlistCount(games);
            }
        });
    });
}

function createWishlistCard(game) {
    const card = document.createElement('article');
    card.className = 'game-card wishlist-game-card';

    const cover = document.createElement('div');
    cover.className = 'game-cover';
    if (game.image) {
        const image = document.createElement('img');
        image.src = game.image;
        image.alt = `Copertina di ${game.title}`;
        image.loading = 'lazy';
        cover.append(image);
    } else {
        const placeholder = document.createElement('div');
        placeholder.className = 'game-image-placeholder';
        placeholder.textContent = '🎮';
        cover.append(placeholder);
    }

    const info = document.createElement('div');
    info.className = 'game-info';
    if (game.type) {
        const badge = document.createElement('span');
        badge.className = 'pill pill-soft';
        badge.textContent = game.type.toUpperCase();
        info.append(badge);
    }
    const heading = document.createElement('h2');
    heading.textContent = game.title;
    const description = document.createElement('p');
    description.className = 'game-summary';
    description.textContent = 'Salvato nella tua wishlist locale.';
    info.append(heading, description);

    const actions = document.createElement('aside');
    actions.className = 'price-card wishlist-actions';
    const label = document.createElement('span');
    label.className = 'price-label';
    label.textContent = game.price ? 'Prezzo al salvataggio' : 'Prezzo';
    const price = document.createElement('strong');
    price.className = game.price ? 'price-value' : 'unavailable';
    const numericPrice = Number(game.price);
    price.textContent = game.price && Number.isFinite(numericPrice) ? `€${numericPrice.toFixed(2)}` : 'Non disponibile';
    actions.append(label, price);
    if (game.shop) {
        const shop = document.createElement('span');
        shop.className = 'shop-name';
        shop.textContent = game.shop;
        actions.append(shop);
    }
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'remove-wishlist-button';
    remove.textContent = 'Rimuovi';
    remove.setAttribute('aria-label', `Rimuovi ${game.title} dalla wishlist`);
    remove.addEventListener('click', () => {
        const games = readWishlist().filter((savedGame) => savedGame.id !== game.id);
        if (writeWishlist(games)) renderWishlist();
    });
    actions.append(remove);

    card.append(cover, info, actions);
    return card;
}

function renderWishlist() {
    const list = document.querySelector('[data-wishlist-list]');
    if (!list) return;

    const games = readWishlist();
    list.replaceChildren(...games.map(createWishlistCard));
    document.querySelector('[data-wishlist-empty]').hidden = games.length > 0;
    updateWishlistCount(games);
}

document.addEventListener('DOMContentLoaded', () => {
    updateWishlistCount();
    initialiseWishlistButtons();
    renderWishlist();
});

window.addEventListener('storage', () => {
    updateWishlistCount();
    renderWishlist();
});

export function renderHeader(el, user) {
  el.innerHTML = `
    <a href="/">Shopfront</a>
    <nav>
      <a href="/settings">Preferences</a>
      ${user ? `<span>${user.name}</span>` : `<a href="/login">Sign in</a>`}
    </nav>`;
}

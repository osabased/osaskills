const PRODUCTS = [
  { id: "p1", name: "Canvas tote", price: 18 },
  { id: "p2", name: "Enamel mug", price: 12 },
  { id: "p3", name: "Wool beanie", price: 24 },
];

export function renderProducts(el) {
  el.innerHTML = PRODUCTS.map(
    (p) => `<article data-id="${p.id}"><h2>${p.name}</h2><p>$${p.price}</p></article>`
  ).join("");
}

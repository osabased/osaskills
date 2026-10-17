import { renderHeader } from "./header.js";
import { renderProducts } from "./products.js";
import { currentUser } from "./auth.js";

renderHeader(document.getElementById("header"), currentUser());
renderProducts(document.getElementById("products"));

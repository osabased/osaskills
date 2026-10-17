import { signIn } from "./auth.js";

export function renderLogin(el) {
  el.innerHTML = `<form><input name="name" placeholder="Your name"><button>Sign in</button></form>`;
  el.querySelector("form").addEventListener("submit", (e) => {
    e.preventDefault();
    signIn(e.target.name.value);
    location.href = "/";
  });
}

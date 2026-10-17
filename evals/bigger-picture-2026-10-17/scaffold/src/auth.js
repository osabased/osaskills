export function currentUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

export function signIn(name) {
  localStorage.setItem("user", JSON.stringify({ id: name.toLowerCase(), name }));
}

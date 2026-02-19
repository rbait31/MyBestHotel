/**
 * Вызовы к backend API.
 * URL API: для локальной разработки — backend на localhost:8000.
 */
const API_BASE = window.API_BASE || "http://127.0.0.1:8000";

async function searchHotels(params) {
  const q = new URLSearchParams();
  if (params.city) q.set("city", params.city);
  if (params.country) q.set("country", params.country);
  if (params.check_in) q.set("check_in", params.check_in);
  const url = `${API_BASE}/api/hotels?${q.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Ошибка запроса");
  }
  return res.json();
}

/**
 * Поиск с AI-анализом (POST /api/search). Нужны check_in и check_out.
 */
async function searchWithAI(body) {
  const res = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Ошибка запроса");
  }
  return res.json();
}

async function getHotelDetails(hotelId, checkIn, checkOut) {
  const q = new URLSearchParams();
  if (checkIn) q.set("check_in", checkIn);
  if (checkOut) q.set("check_out", checkOut);
  const url = `${API_BASE}/api/hotels/${hotelId}?${q.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Ошибка запроса");
  }
  return res.json();
}

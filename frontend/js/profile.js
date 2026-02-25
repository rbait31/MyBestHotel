/**
 * Профиль путешественника: API (PostgreSQL) с fallback на localStorage.
 */
const PROFILE_KEY = "mybesthotel_profile";
const USER_ID_KEY = "mybesthotel_user_id";

function getUserId() {
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
}

const defaultProfile = () => ({
  trip_type: "leisure",
  budget_min: null,
  budget_max: null,
  with_car: false,
  with_pets: false,
  themes: ["cleanliness", "location", "noise", "internet"],
  // Предпочтения (0–5)
  preference_center: 3,
  preference_breakfast: 3,
  preference_cleanliness: 3,
  preference_quiet: 3,
  preference_wifi: 3,
  preference_nature: 3,
  // Анкета
  solo: false,
  couple: false,
  family: false,
  group: false,
  // Red Flags (критично)
  red_flag_safety: false,
  red_flag_dirt: false,
  red_flag_noise_night: false,
  red_flag_weak_wifi: false,
  red_flag_no_car_access: false,
  red_flag_insects: false,
  red_flag_scam: false,
});

function migrateProfile(p) {
  const m = { ...defaultProfile(), ...p };
  if ("breakfast_included" in p && typeof p.breakfast_included === "boolean" && !("preference_breakfast" in p)) {
    m.preference_breakfast = p.breakfast_included ? 5 : 0;
  }
  return m;
}

function loadProfileLocal() {
  try {
    const raw = localStorage.getItem(PROFILE_KEY);
    if (!raw) return defaultProfile();
    const p = JSON.parse(raw);
    return migrateProfile(p);
  } catch {
    return defaultProfile();
  }
}

function saveProfileLocal(profile) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

async function loadProfileFromAPI() {
  const base = window.API_BASE || "http://127.0.0.1:8000";
  const userId = getUserId();
  const r = await fetch(`${base}/api/profile?user_id=${encodeURIComponent(userId)}`, { method: "GET" });
  if (!r.ok) return null;
  const data = await r.json();
  return data?.profile ? migrateProfile(data.profile) : null;
}

async function saveProfileToAPI(profile) {
  const base = window.API_BASE || "http://127.0.0.1:8000";
  const userId = getUserId();
  const r = await fetch(`${base}/api/profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, profile }),
  });
  return r.ok;
}

/**
 * Загрузить профиль: сначала API, при ошибке — localStorage.
 */
async function loadProfile() {
  try {
    const p = await loadProfileFromAPI();
    if (p) {
      saveProfileLocal(p);
      return p;
    }
  } catch (_) {}
  return loadProfileLocal();
}

/**
 * Сохранить профиль: сначала API, при ошибке — localStorage.
 */
async function saveProfile(profile) {
  try {
    const ok = await saveProfileToAPI(profile);
    if (ok) {
      saveProfileLocal(profile);
      return true;
    }
  } catch (_) {}
  saveProfileLocal(profile);
  return false;
}

function exportProfileJSON(profile) {
  return JSON.stringify(profile, null, 2);
}

async function importProfileJSON(jsonString) {
  try {
    const p = JSON.parse(jsonString);
    if (typeof p !== "object" || p === null) return null;
    const merged = migrateProfile(p);
    await saveProfile(merged);
    return merged;
  } catch {
    return null;
  }
}

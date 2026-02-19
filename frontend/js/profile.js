/**
 * Профиль путешественника: localStorage, export/import JSON.
 */
const PROFILE_KEY = "mybesthotel_profile";

const defaultProfile = () => ({
  trip_type: "leisure",
  budget_min: null,
  budget_max: null,
  with_car: false,
  with_pets: false,
  comfort_level: "comfort",
  themes: ["cleanliness", "location", "noise", "internet"],
});

function loadProfile() {
  try {
    const raw = localStorage.getItem(PROFILE_KEY);
    if (!raw) return defaultProfile();
    const p = JSON.parse(raw);
    return { ...defaultProfile(), ...p };
  } catch {
    return defaultProfile();
  }
}

function saveProfile(profile) {
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

function exportProfileJSON(profile) {
  return JSON.stringify(profile, null, 2);
}

function importProfileJSON(jsonString) {
  try {
    const p = JSON.parse(jsonString);
    if (typeof p !== "object" || p === null) return null;
    saveProfile({ ...defaultProfile(), ...p });
    return loadProfile();
  } catch {
    return null;
  }
}

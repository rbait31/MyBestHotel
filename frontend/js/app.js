/**
 * My Best Hotel — основная логика приложения (Alpine.js data).
 * Город → страна (однозначно)
 */
const CITIES = [
  { value: "Paris", label: "Paris", searchTerms: ["paris", "париж"] },
  { value: "Barcelona", label: "Barcelona", searchTerms: ["barcelona", "барселона"] },
  { value: "Madrid", label: "Madrid", searchTerms: ["madrid", "мадрид"] },
];
const CITY_TO_COUNTRY = {
  Paris: "France",
  Barcelona: "Spain",
  Madrid: "Spain",
};
/** Город → [страны/штаты], если город есть в нескольких странах */
const CITY_TO_MULTIPLE = {};
/** Все страны для fallback (неизвестный город) */
const ALL_COUNTRIES = ["France", "Spain"];

function app() {
  return {
    city: "",
    cityInput: "",
    citySuggestions: [],
    cityDropdownOpen: false,
    country: "",
    check_in: "",
    check_out: "",
    searchBudgetMin: null,
    searchBudgetMax: null,
    profile: defaultProfile(),
    hotels: [],
    loading: false,
    error: "",
    invalidFields: { city: false, country: false, check_in: false, check_out: false },
    backendOk: null,
    lastSearched: false,
    countryOptions: [],
    countryLocked: false,

    get minCheckIn() {
      return new Date().toISOString().slice(0, 10);
    },
    get minCheckOut() {
      if (!this.check_in) return this.minCheckIn;
      const d = new Date(this.check_in + "T12:00:00");
      d.setDate(d.getDate() + 1);
      return d.toISOString().slice(0, 10);
    },
    get isCheckInToday() {
      return this.check_in && this.check_in === this.minCheckIn;
    },

    getEffectiveBudgetMin() {
      const v = this.searchBudgetMin;
      if (v != null && v !== "" && !isNaN(Number(v))) return Number(v);
      return this.profile?.budget_min ?? null;
    },
    getEffectiveBudgetMax() {
      const v = this.searchBudgetMax;
      if (v != null && v !== "" && !isNaN(Number(v))) return Number(v);
      return this.profile?.budget_max ?? null;
    },

    get profileSummary() {
      const p = this.profile || {};
      const parts = [];
      const tripLabels = { leisure: "Отдых", business: "Бизнес" };
      parts.push(tripLabels[p.trip_type] || "Отдых");
      const effMin = this.getEffectiveBudgetMin();
      const effMax = this.getEffectiveBudgetMax();
      if (effMin != null && effMin > 0) {
        parts.push("бюджет от €" + effMin + "/ночь");
      }
      if (effMax != null && effMax > 0) {
        parts.push("до €" + effMax + "/ночь");
      }
      const prefLabels = {
        preference_center: "центр",
        preference_breakfast: "завтрак",
        preference_cleanliness: "чистота",
        preference_quiet: "тишина",
        preference_wifi: "Wi‑Fi",
        preference_nature: "природа",
      };
      const important = [];
      for (const [key, label] of Object.entries(prefLabels)) {
        if ((p[key] ?? 3) >= 4) important.push(label);
      }
      if (important.length) {
        parts.push("важно: " + important.join(", "));
      }
      return parts.length ? parts.join(" · ") : null;
    },

    onCityInput(val) {
      this.cityInput = val;
      this.cityDropdownOpen = true;
      const q = (val || "").trim().toLowerCase();
      if (!q) {
        this.citySuggestions = CITIES.map((c) => ({ value: c.value, label: c.label }));
        return;
      }
      this.citySuggestions = CITIES.filter((c) =>
        c.searchTerms.some((t) => t.startsWith(q) || c.label.toLowerCase().startsWith(q))
      ).map((c) => ({ value: c.value, label: c.label }));
    },

    selectCity(value) {
      const c = CITIES.find((x) => x.value === value);
      if (c) {
        this.cityInput = c.label;
        this.city = c.value;
        this.cityDropdownOpen = false;
        this.onCityChange(c.value);
      }
    },

    onCityFocus() {
      this.cityDropdownOpen = true;
      if (!this.cityInput.trim()) {
        this.citySuggestions = CITIES.map((c) => ({ value: c.value, label: c.label }));
      }
    },

    async init() {
      this.profile = await loadProfile();
      this.searchBudgetMin = this.profile.budget_min ?? null;
      this.searchBudgetMax = this.profile.budget_max ?? null;
      this.citySuggestions = CITIES.map((c) => ({ value: c.value, label: c.label }));
      this.$watch("city", (value) => this.onCityChange(value));
      this.onCityChange(this.city);
      try {
        const r = await fetch((window.API_BASE || "http://127.0.0.1:8000") + "/", { method: "GET" });
        this.backendOk = r.ok;
      } catch {
        this.backendOk = false;
      }
    },

    onCityChange(city) {
      if (!city || !city.trim()) {
        this.country = "";
        this.countryOptions = [];
        this.countryLocked = false;
        return;
      }
      const c = city.trim();
      if (CITY_TO_COUNTRY[c]) {
        const label = CITIES.find((x) => x.value === c)?.label || c;
        if (this.cityInput !== label) this.cityInput = label;
        const cnt = CITY_TO_COUNTRY[c];
        this.countryOptions = [cnt];
        this.countryLocked = true;
        this.country = cnt;
      } else if (CITY_TO_MULTIPLE[c]) {
        this.countryOptions = CITY_TO_MULTIPLE[c];
        this.countryLocked = false;
        if (!this.country || !this.countryOptions.includes(this.country)) {
          this.country = this.countryOptions[0];
        }
      } else {
        this.countryOptions = ALL_COUNTRIES;
        this.countryLocked = false;
        this.country = "";
      }
    },

    validateDates() {
      const today = new Date().toISOString().slice(0, 10);
      if (!this.check_in) return { valid: false, error: "Введите дату заезда", invalidCheckIn: true, invalidCheckOut: false };
      if (!this.check_out) return { valid: false, error: "Введите дату выезда", invalidCheckIn: false, invalidCheckOut: true };
      if (this.check_in < today) {
        return { valid: false, error: "Дата заезда не может быть в прошлом", invalidCheckIn: true, invalidCheckOut: false };
      }
      if (this.check_out <= this.check_in) {
        return { valid: false, error: "Дата выезда должна быть позже даты заезда", invalidCheckIn: false, invalidCheckOut: true };
      }
      return { valid: true, error: "", invalidCheckIn: false, invalidCheckOut: false };
    },

    async runSearch() {
      this.error = "";
      const validCity = CITIES.some((c) => c.value === this.city);
      if (!validCity) {
        this.city = "";
        this.cityInput = this.cityInput.trim();
      }
      const emptyCity = !validCity || !this.city.trim();
      const emptyCountry = !this.country.trim();
      const dateValidation = this.validateDates();
      const empty = {
        city: emptyCity,
        country: emptyCountry,
        check_in: !this.check_in || dateValidation.invalidCheckIn,
        check_out: !this.check_out || dateValidation.invalidCheckOut,
      };
      this.invalidFields = empty;
      if (emptyCity || emptyCountry) {
        this.error = "Введите все данные!";
        document.getElementById("msg-error")?.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
      }
      if (!dateValidation.valid) {
        this.error = dateValidation.error;
        document.getElementById("msg-error")?.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
      }
      this.loading = true;
      this.lastSearched = false;
      try {
        const profileForSearch = { ...this.profile };
        const effMin = this.getEffectiveBudgetMin();
        const effMax = this.getEffectiveBudgetMax();
        profileForSearch.budget_min = effMin;
        profileForSearch.budget_max = effMax;
        const body = {
          city: this.city.trim(),
          country: this.country.trim(),
          check_in: this.check_in,
          check_out: this.check_out,
          profile: profileForSearch,
        };
        const data = await searchWithAI(body);
        this.hotels = data.hotels || [];
        this.lastSearched = true;
        if (this.hotels.length > 0) {
          document.getElementById("results")?.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      } catch (e) {
        this.lastSearched = true;
        const msg = e.message || "Ошибка запроса";
        this.error = msg.toLowerCase().includes("fetch") || msg === "Failed to fetch"
          ? "Сервер недоступен. Запустите бэкенд: uvicorn backend.main:app --reload"
          : msg;
        this.hotels = [];
        document.getElementById("msg-error")?.scrollIntoView({ behavior: "smooth", block: "center" });
      } finally {
        this.loading = false;
      }
    },

  };
}

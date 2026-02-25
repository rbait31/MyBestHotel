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
    profile: defaultProfile(),
    hotels: [],
    loading: false,
    error: "",
    invalidFields: { city: false, country: false, check_in: false, check_out: false },
    backendOk: null,
    lastSearched: false,
    countryOptions: [],
    countryLocked: false,

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

    async runSearch() {
      this.error = "";
      const validCity = CITIES.some((c) => c.value === this.city);
      if (!validCity) {
        this.city = "";
        this.cityInput = this.cityInput.trim();
      }
      const empty = {
        city: !validCity || !this.city.trim(),
        country: !this.country.trim(),
        check_in: !this.check_in,
        check_out: !this.check_out,
      };
      this.invalidFields = empty;
      const hasEmpty = empty.city || empty.country || empty.check_in || empty.check_out;
      if (hasEmpty) {
        this.error = "Введите все данные!";
        return;
      }
      this.loading = true;
      this.lastSearched = false;
      try {
        const body = {
          city: this.city.trim(),
          country: this.country.trim(),
          check_in: this.check_in,
          check_out: this.check_out,
          profile: this.profile,
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

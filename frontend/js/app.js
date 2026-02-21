/**
 * My Best Hotel — основная логика приложения (Alpine.js data).
 * Город → страна (однозначно)
 */
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
    /** Варианты для селектора страны */
    countryOptions: [],
    /** true — страна подставлена автоматически, селектор заблокирован */
    countryLocked: false,

    async init() {
      this.profile = loadProfile();
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
        this.country = CITY_TO_COUNTRY[c];
        this.countryOptions = [CITY_TO_COUNTRY[c]];
        this.countryLocked = true;
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
      const empty = {
        city: !this.city.trim(),
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
          profile: {
            trip_type: this.profile.trip_type,
            budget_min: this.profile.budget_min,
            budget_max: this.profile.budget_max,
            with_car: this.profile.with_car,
            with_pets: this.profile.with_pets,
            comfort_level: this.profile.comfort_level,
            themes: this.profile.themes || [],
          },
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

    saveProfile() {
      saveProfile(this.profile);
      this.error = "";
      alert("Профиль сохранён в браузере.");
    },

    exportProfile() {
      const json = exportProfileJSON(this.profile);
      const blob = new Blob([json], { type: "application/json" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "mybesthotel-profile.json";
      a.click();
      URL.revokeObjectURL(a.href);
    },

    importProfile(event) {
      const file = event.target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        const next = importProfileJSON(reader.result);
        if (next) {
          this.profile = next;
          alert("Профиль загружен.");
        } else {
          alert("Неверный JSON.");
        }
      };
      reader.readAsText(file);
      event.target.value = "";
    },
  };
}

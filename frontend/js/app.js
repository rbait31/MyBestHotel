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

/** Отели в системе (3 на город для подсказки). Полный список для autocomplete. */
const HOTELS = [
  { id: "hotel_001", name: "Grand Plaza", city: "Paris", searchTerms: ["grand", "plaza", "гранд", "плаза"] },
  { id: "hotel_002", name: "Cozy Inn", city: "Paris", searchTerms: ["cozy", "inn", "кози"] },
  { id: "hotel_003", name: "Le Marais Boutique", city: "Paris", searchTerms: ["le", "marais", "boutique", "маре", "бутик"] },
  { id: "hotel_004", name: "Budget Stay Paris", city: "Paris", searchTerms: ["budget", "stay", "париж"] },
  { id: "hotel_005", name: "Louvre View Hotel", city: "Paris", searchTerms: ["louvre", "view", "hotel", "лувр"] },
  { id: "hotel_006", name: "Casa Mediterranea", city: "Barcelona", searchTerms: ["casa", "mediterranea", "каса"] },
  { id: "hotel_007", name: "Gothic Quarter Inn", city: "Barcelona", searchTerms: ["gothic", "quarter", "inn", "готический"] },
  { id: "hotel_008", name: "Beach Front Barcelona", city: "Barcelona", searchTerms: ["beach", "front", "барселона"] },
  { id: "hotel_009", name: "Hostal San Lorenzo", city: "Madrid", searchTerms: ["hostal", "san", "lorenzo", "лоренсо"] },
  { id: "hotel_010", name: "Hostal Abadia Madrid", city: "Madrid", searchTerms: ["hostal", "abadia", "мадрид"] },
  { id: "hotel_011", name: "Ibis Styles Madrid Prado", city: "Madrid", searchTerms: ["ibis", "styles", "prado", "прадо"] },
  { id: "hotel_012", name: "Hostal Oriente", city: "Madrid", searchTerms: ["hostal", "oriente", "ориенте"] },
  { id: "hotel_013", name: "Motion Chueca Hostel", city: "Madrid", searchTerms: ["motion", "chueca", "hostel"] },
  { id: "hotel_014", name: "Generator Madrid", city: "Madrid", searchTerms: ["generator", "мадрид"] },
  { id: "hotel_015", name: "The Hat Madrid", city: "Madrid", searchTerms: ["hat", "мадрид"] },
  { id: "hotel_016", name: "Hostal Persal", city: "Madrid", searchTerms: ["hostal", "persal"] },
  { id: "hotel_017", name: "Boutique Apartments in the Heart of Madrid", city: "Madrid", searchTerms: ["boutique", "apartments", "heart", "мадрид"] },
  { id: "hotel_018", name: "4 Bears Sharehome", city: "Madrid", searchTerms: ["bears", "sharehome"] },
  { id: "hotel_019", name: "Líbere Madrid Palacio Real", city: "Madrid", searchTerms: ["libere", "palacio", "real"] },
  { id: "hotel_020", name: "B&B Hotel Madrid Centro Plaza Mayor", city: "Madrid", searchTerms: ["bb", "plaza", "mayor", "майор"] },
  { id: "hotel_021", name: "DAS CARRETAS", city: "Madrid", searchTerms: ["das", "carretas"] },
  { id: "hotel_022", name: "Hostal Veracruz – Puerta del Sol", city: "Madrid", searchTerms: ["hostal", "veracruz", "puerta", "sol"] },
  { id: "hotel_023", name: "Hostal Buenos Aires Gran Via", city: "Madrid", searchTerms: ["hostal", "buenos", "aires", "gran", "via"] },
  { id: "hotel_024", name: "Hostal Atocha 28", city: "Madrid", searchTerms: ["hostal", "atocha"] },
  { id: "hotel_025", name: "Hotel Urban", city: "Madrid", searchTerms: ["hotel", "urban"] },
  { id: "hotel_026", name: "NH Collection Madrid Gran Vía", city: "Madrid", searchTerms: ["nh", "collection", "gran", "via"] },
  { id: "hotel_027", name: "Hotel Liabeny", city: "Madrid", searchTerms: ["hotel", "liabeny"] },
  { id: "hotel_028", name: "Catalonia Puerta del Sol", city: "Madrid", searchTerms: ["catalonia", "puerta", "sol"] },
  { id: "hotel_029", name: "Vincci Soho", city: "Madrid", searchTerms: ["vincci", "soho"] },
  { id: "hotel_030", name: "Room Mate Alba", city: "Madrid", searchTerms: ["room", "mate", "alba"] },
];

const HOTEL_HINT_EXAMPLES = {
  Paris: ["Grand Plaza", "Cozy Inn", "Le Marais Boutique"],
  Barcelona: ["Casa Mediterranea", "Gothic Quarter Inn", "Beach Front Barcelona"],
  Madrid: ["Hostal San Lorenzo", "Ibis Styles Madrid Prado", "The Hat Madrid"],
};

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
    checkHotelInput: "",
    checkHotelName: "",
    hotelSuggestions: [],
    hotelDropdownOpen: false,
    checkedHotel: null,
    checkHotelLoading: false,
    checkHotelError: "",
    invalidFields: { city: false, country: false, check_in: false, check_out: false },
    backendOk: null,
    lastSearched: false,
    lastChecked: false,
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
        parts.push("от €" + effMin + "/ночь");
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

    get profileSummaryForCheck() {
      const p = this.profile || {};
      const parts = [];
      const tripLabels = { leisure: "Отдых", business: "Бизнес" };
      parts.push(tripLabels[p.trip_type] || "Отдых");
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
      await this.syncProfileFromStorage();
      this.citySuggestions = CITIES.map((c) => ({ value: c.value, label: c.label }));
      this.hotelSuggestions = HOTELS.map((h) => ({ value: h.name, label: h.name, city: h.city }));
      this.$watch("city", (value) => this.onCityChange(value));
      this.onCityChange(this.city);
      try {
        const r = await fetch((window.API_BASE || "http://127.0.0.1:8000") + "/", { method: "GET" });
        this.backendOk = r.ok;
      } catch {
        this.backendOk = false;
      }
      window.addEventListener('pageshow', (event) => {
        if (event.persisted) this.syncProfileFromStorage();
      });
    },

    async syncProfileFromStorage() {
      this.profile = await loadProfile();
      this.searchBudgetMin = this.profile.budget_min ?? null;
      this.searchBudgetMax = this.profile.budget_max ?? null;
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

    onHotelInput(val) {
      this.checkHotelInput = val;
      this.hotelDropdownOpen = true;
      const q = (val || "").trim().toLowerCase();
      let list = HOTELS;
      if (this.city) {
        list = list.filter((h) => h.city === this.city);
      }
      if (!q) {
        this.hotelSuggestions = list.map((h) => ({ value: h.name, label: h.name, city: h.city }));
        return;
      }
      this.hotelSuggestions = list
        .filter(
          (h) =>
            h.name.toLowerCase().includes(q) ||
            h.searchTerms.some((t) => t.startsWith(q) || t.includes(q))
        )
        .map((h) => ({ value: h.name, label: h.name, city: h.city }));
    },

    selectHotel(name) {
      const h = HOTELS.find((x) => x.name === name);
      if (h) {
        this.checkHotelInput = h.name;
        this.checkHotelName = h.name;
        this.hotelDropdownOpen = false;
      }
    },

    onHotelFocus() {
      this.hotelDropdownOpen = true;
      let list = HOTELS;
      if (this.city) list = list.filter((h) => h.city === this.city);
      this.hotelSuggestions = list.map((h) => ({ value: h.name, label: h.name, city: h.city }));
    },

    get hotelHintText() {
      const parts = [];
      for (const [city, names] of Object.entries(HOTEL_HINT_EXAMPLES)) {
        parts.push(city + " — " + names.join(", "));
      }
      return "Сейчас в системе рассматриваются отели: " + parts.join("; ");
    },

    async runCheckHotel() {
      const missing = [];
      if (!this.city?.trim()) missing.push("Город");
      if (!this.country?.trim()) missing.push("Страна");
      if (!this.check_in?.trim()) missing.push("Дата заезда");
      if (!this.check_out?.trim()) missing.push("Дата выезда");
      if (missing.length > 0) {
        this.checkHotelError = "Заполните обязательные поля поиска: " + missing.join(", ");
        return;
      }

      const name = (this.checkHotelName || this.checkHotelInput || "").trim();
      const validHotel = HOTELS.some((h) => h.name === name);
      if (!name) {
        this.checkHotelError = "Введите название отеля";
        return;
      }
      if (!validHotel) {
        this.checkHotelError = "Выберите отель из списка";
        return;
      }
      this.checkHotelError = "";
      this.checkHotelLoading = true;
      this.checkedHotel = null;
      try {
        const profileForCheck = { ...this.profile };
        profileForCheck.budget_min = this.getEffectiveBudgetMin();
        profileForCheck.budget_max = this.getEffectiveBudgetMax();
        const data = await checkHotel({
          hotel_name: name.trim(),
          city: this.city || "",
          country: this.country || "",
          profile: profileForCheck,
        });
        this.checkedHotel = data;
        this.lastChecked = true;
        document.querySelector("#check-hotel-result")?.scrollIntoView({ behavior: "smooth", block: "start" });
      } catch (e) {
        this.checkHotelError = e.message || "Ошибка запроса";
      } finally {
        this.checkHotelLoading = false;
      }
    },

  };
}

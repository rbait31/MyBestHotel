/**
 * Сохранение карточки отеля в .md — без зависимостей, для my-choice.html и index.html.
 */
function hotelToMarkdown(hotel) {
  if (!hotel) return "";
  const h = hotel;
  const lines = [];
  lines.push("# " + (h.name || "Отель"));
  lines.push("");
  if (h.district || h.rating != null) {
    const meta = [h.district, h.rating != null ? "Рейтинг " + h.rating : null].filter(Boolean).join(" · ");
    lines.push(meta);
    lines.push("");
  }
  if (h.final_score != null) {
    lines.push("**Итоговая оценка:** " + h.final_score + "/10");
    lines.push("");
  }
  if (h.price_per_night != null) {
    lines.push("**Цена:** €" + Number(h.price_per_night).toFixed(0) + " / ночь");
    lines.push("");
  }
  if (h.location_score != null) {
    lines.push("**Локация:** " + h.location_score + "/10");
    lines.push("");
  }
  if (h.quality_score != null) {
    lines.push("**Оценка:** " + h.quality_score + (h.value_for_money != null ? " · Value: " + h.value_for_money : ""));
    lines.push("");
  }
  if (h.consistency_score != null && h.consistency_score < 0.6) {
    lines.push("**Согласованность отзывов:** " + Math.round((h.consistency_score || 0) * 100) + "% — отзывы могут противоречить друг другу");
    lines.push("");
  }
  if (h.red_flags && h.red_flags.length) {
    lines.push("⚠ **Критично:** " + h.red_flags.join(", "));
    lines.push("");
  }
  if (h.pros && h.pros.length) {
    lines.push("**Плюсы:** " + h.pros.join("; "));
    lines.push("");
  }
  if (h.cons && h.cons.length) {
    lines.push("**Минусы:** " + h.cons.join("; "));
    lines.push("");
  }
  if (h.verdict) {
    lines.push("*" + h.verdict + "*");
    lines.push("");
  }
  lines.push("---");
  lines.push("*My Best Hotel — выбор отеля по отзывам и профилю*");
  return lines.join("\n");
}

function downloadHotelCard(hotel) {
  const md = hotelToMarkdown(hotel);
  const name = (hotel?.name || "hotel").replace(/[^\w\s\-а-яА-ЯёЁ]/gi, "").replace(/\s+/g, "-").slice(0, 40) || "hotel";
  const filename = (hotel?.id || name) + "-" + name + ".md";
  const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

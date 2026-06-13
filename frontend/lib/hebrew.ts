const labels: Record<string, string> = {
  draft: "טיוטה",
  uploading: "מעלה קבצים",
  ready: "מוכן",
  generating: "בתהליך יצירה",
  review: "מוכן לבדיקה",
  published: "פורסם",
  archived: "בארכיון",
  queued: "ממתין בתור",
  completed: "הושלם",
  failed: "נכשל",
  cancelled: "בוטל",
  electronics: "אלקטרוניקה",
  appliance: "מכשירי חשמל",
  furniture: "ריהוט ועיצוב",
  packaging: "אריזות",
  industrial: "ציוד תעשייתי",
  automotive: "רכב",
  fashion: "אופנה",
  other: "אחר",
  commercial: "מסחרי",
  engineering: "הנדסי",
  standard: "רגילה",
  restricted: "מוגבלת",
  private: "פרטית",
  point: "נקודתית",
  directional: "כיוונית",
  enclosure: "מעטפת",
  button: "כפתור",
  switch: "מתג",
  door: "דלת",
};

export function heLabel(value?: string | null) {
  if (!value) return "לא צוין";
  return labels[value.toLowerCase()] || value;
}

export function formatDateHe(value: string) {
  return new Date(value).toLocaleDateString("he-IL");
}

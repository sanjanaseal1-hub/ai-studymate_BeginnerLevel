// Frontend validation: quick feedback. The backend validates again.
export const MAX_CONTENT_CHARS = 8000;

export function validateInput(content, options, utility) {
  if (!content.trim()) return "Please enter some study material first.";
  if (content.length > MAX_CONTENT_CHARS)
    return `Your text is too long. Please keep it under ${MAX_CONTENT_CHARS} characters.`;
  for (const field of utility.options) {
    const value = options[field.name];
    if (field.type === "number") {
      const n = Number(value);
      if (!Number.isInteger(n) || n < field.min || n > field.max)
        return `${field.label} must be a whole number from ${field.min} to ${field.max}.`;
    }
    if (field.type === "select" && !field.choices.includes(value)) return `Please choose a valid ${field.label.toLowerCase()}.`;
  }
  return null;
}

// Build the request body: numbers become numbers, empty optional fields are dropped.
export function buildOptions(options, utility) {
  const out = {};
  for (const field of utility.options) {
    const value = options[field.name];
    if (value === undefined || String(value).trim() === "") continue;
    out[field.name] = field.type === "number" ? Number(value) : String(value).trim();
  }
  return out;
}

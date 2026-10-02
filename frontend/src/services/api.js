// The only file that talks to the backend. Throws Error(userFriendlyMessage) on failure.
const BASE_URL = import.meta.env.VITE_API_URL || ""; // empty = use the Vite dev proxy
const TIMEOUT_MS = 60000;

export async function generate(endpoint, content, options) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(`${BASE_URL}/api/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, options }),
      signal: controller.signal,
    });
    let data = null;
    try { data = await response.json(); } catch { /* not JSON */ }
    if (!response.ok || !data?.success) {
      throw new Error(data?.error || "Unable to generate the response right now. Please try again.");
    }
    return data.result;
  } catch (err) {
    if (err.name === "AbortError") throw new Error("The request took too long. Please try again.");
    if (err instanceof TypeError) throw new Error("Cannot reach the server. Check your connection and try again.");
    throw err; // already a friendly Error from above
  } finally {
    clearTimeout(timer);
  }
}

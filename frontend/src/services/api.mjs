export class APIError extends Error {
  constructor(message, code, status) {
    super(message);
    this.name = "APIError";
    this.code = code;
    this.status = status;
  }
}
export async function request(path, { body, signal } = {}) {
  const timeout = AbortSignal.timeout(35000);
  const combinedSignal = signal ? AbortSignal.any([signal, timeout]) : timeout;
  let response;
  try {
    response = await fetch(`/api${path}`, {
      method: body ? "POST" : "GET",
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: combinedSignal,
    });
  } catch (error) {
    if (signal?.aborted) throw error;
    throw new APIError(
      error.name === "TimeoutError"
        ? "El análisis tardó más de lo esperado. Intenta nuevamente."
        : "No se pudo conectar con la API. Revisa que el nodo esté disponible.",
      "CONNECTION_ERROR",
      0,
    );
  }
  let data;
  try {
    data = await response.json();
  } catch {
    throw new APIError(
      "La API no devolvió un documento JSON válido.",
      "INVALID_RESPONSE",
      response.status,
    );
  }
  if (!response.ok)
    throw new APIError(
      data.message || "No se pudo completar la solicitud.",
      data.error || "API_ERROR",
      response.status,
    );
  return data;
}
export const api = {
  meta: (signal) => request("/meta", { signal }),
  locations: (signal) => request("/locations", { signal }),
  sources: (signal) => request("/sources", { signal }),
  layers: (signal) => request("/layers", { signal }),
  analyze: (location, project_type, signal) =>
    request("/analyze", { body: { location, project_type }, signal }),
  compare: (location_a, location_b, project_type, signal) =>
    request("/compare", {
      body: { location_a, location_b, project_type },
      signal,
    }),
};

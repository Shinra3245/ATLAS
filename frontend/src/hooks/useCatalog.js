import { useEffect, useState, useCallback } from "react";
import { api } from "../services/api.mjs";

export function useCatalog() {
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState({
    locations: [],
    sources: [],
    layers: [],
    meta: null,
    loading: true,
    error: null,
  });
  useEffect(() => {
    const controller = new AbortController();
    setState((s) => ({ ...s, loading: true, error: null }));
    Promise.all([
      api.locations(controller.signal),
      api.sources(controller.signal),
      api.layers(controller.signal),
      api.meta(controller.signal),
    ])
      .then(([locations, sources, layers, meta]) => {
        if (!Array.isArray(locations.locations) || !locations.locations.length)
          throw new Error(
            "La API aún no publica localidades. No se usarán datos simulados.",
          );
        setState({
          locations: locations.locations,
          sources: sources.sources || [],
          layers: layers.layers || [],
          meta,
          loading: false,
          error: null,
        });
      })
      .catch((error) => {
        if (!controller.signal.aborted)
          setState((s) => ({ ...s, loading: false, error: error.message }));
      });
    return () => controller.abort();
  }, [revision]);
  const retry = useCallback(() => setRevision((n) => n + 1), []);
  return { ...state, retry };
}

import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Compass, LocateFixed, Layers } from "lucide-react";
import { GeoPulse } from "../components/GeoPulse";

const OVERVIEW = [20.62, -101.06];

function prefersReducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function convexHull(latlngs) {
  const unique = [];
  for (const point of latlngs) {
    if (!unique.some((item) => item[0] === point[0] && item[1] === point[1]))
      unique.push(point);
  }
  const pts = unique
    .map(([lat, lng]) => [lng, lat])
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  if (pts.length < 3) return unique;
  const cross = (o, a, b) =>
    (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const build = (source) => {
    const ring = [];
    for (const point of source) {
      while (
        ring.length >= 2 &&
        cross(ring[ring.length - 2], ring[ring.length - 1], point) <= 0
      )
        ring.pop();
      ring.push(point);
    }
    ring.pop();
    return ring;
  };
  return build(pts)
    .concat(build([...pts].reverse()))
    .map(([lng, lat]) => [lat, lng]);
}

function expandRing(ring, amount = 0.14) {
  if (ring.length < 3) return ring;
  const lat = ring.reduce((sum, point) => sum + point[0], 0) / ring.length;
  const lng = ring.reduce((sum, point) => sum + point[1], 0) / ring.length;
  return ring.map(([y, x]) => [
    lat + (y - lat) * (1 + amount),
    lng + (x - lng) * (1 + amount),
  ]);
}

function zonesFrom(locations) {
  const groups = new Map();
  for (const record of locations) {
    if (!Number.isFinite(record.latitude) || !Number.isFinite(record.longitude))
      continue;
    const name = record.municipality;
    if (!name) continue;
    if (!groups.has(name)) groups.set(name, []);
    groups.get(name).push([record.latitude, record.longitude]);
  }
  return [...groups.entries()].map(([name, points]) => ({
    name,
    ring: expandRing(convexHull(points)),
  }));
}

export function TerritoryMap({
  locations = [],
  selectedA,
  selectedB,
  onSelect,
  municipality,
  focusedMunicipality = null,
  onChooseZone,
  mini = false,
}) {
  const container = useRef(null);
  const mapRef = useRef(null);
  const pointsRef = useRef(null);
  const zonesRef = useRef(null);
  const selectionRef = useRef(null);
  const handlerRef = useRef(onSelect);
  const zoneHandlerRef = useRef(onChooseZone);
  const seenFocus = useRef(false);
  const [offline, setOffline] = useState(false);
  const [tilesEnabled, setTilesEnabled] = useState(true);
  const [mapLoading, setMapLoading] = useState(true);
  const tileRef = useRef(null);
  const baseReadyRef = useRef(false);
  const stopLoadingRef = useRef(null);
  handlerRef.current = onSelect;
  zoneHandlerRef.current = onChooseZone;

  useEffect(() => {
    baseReadyRef.current = false;
    let active = true;
    let loadingTimer;
    const map = L.map(container.current, {
      zoomControl: !mini,
      scrollWheelZoom: !mini,
      dragging: !mini,
      doubleClickZoom: !mini,
      keyboard: !mini,
      touchZoom: !mini,
      attributionControl: true,
    }).setView(OVERVIEW, mini ? 9 : 10);
    mapRef.current = map;
    if (!mini) {
      L.control.scale({ imperial: false, position: "bottomleft" }).addTo(map);
    }
    const tiles = L.tileLayer(
      "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
        maxZoom: 18,
      },
    );
    let failures = 0;
    function stopLoading() {
      window.clearTimeout(loadingTimer);
      loadingTimer = null;
      if (active) setMapLoading(false);
    }
    function unavailable() {
      if (!active) return;
      stopLoading();
      setOffline(true);
      setTilesEnabled(false);
      if (map.hasLayer(tiles)) map.removeLayer(tiles);
      baseReadyRef.current = false;
    }
    stopLoadingRef.current = stopLoading;
    tiles.on("loading", () => {
      failures = 0;
      // After the first usable map, panning/zooming loads tiles quietly.
      if (!active || baseReadyRef.current) return;
      setMapLoading(true);
      setOffline(false);
      if (!loadingTimer) loadingTimer = window.setTimeout(unavailable, 12000);
    });
    tiles.on("load", () => {
      if (!active || !map.hasLayer(tiles)) return;
      stopLoading();
      baseReadyRef.current = true;
    });
    tiles.on("tileerror", () => {
      if (!active || !map.hasLayer(tiles)) return;
      failures++;
      if (failures >= 3) unavailable();
    });
    tiles.on("tileload", () => {
      if (active && map.hasLayer(tiles)) setOffline(false);
    });
    tiles.addTo(map);
    tileRef.current = tiles;
    zonesRef.current = L.layerGroup().addTo(map);
    pointsRef.current = L.layerGroup().addTo(map);
    selectionRef.current = L.layerGroup().addTo(map);
    const observer = new ResizeObserver(() =>
      map.invalidateSize({ animate: false }),
    );
    observer.observe(container.current);
    return () => {
      active = false;
      window.clearTimeout(loadingTimer);
      stopLoadingRef.current = null;
      tiles.off();
      observer.disconnect();
      map.remove();
      mapRef.current = null;
    };
  }, [mini]);

  useEffect(() => {
    const map = mapRef.current;
    const zones = zonesRef.current;
    const points = pointsRef.current;
    if (!map || !zones || !points || mini) return;
    const reduce = prefersReducedMotion();
    const territory = zonesFrom(locations);
    const pins = [selectedA, selectedB].filter(Boolean);
    let cancelled = false;

    function paintZones(interactive) {
      zones.clearLayers();
      for (const zone of territory) {
        if (
          focusedMunicipality &&
          zone.name !== focusedMunicipality
        )
          continue;
        const polygon = L.polygon(zone.ring, {
          className: interactive ? "available-zone" : "available-zone is-quiet",
          color: "#0c7c8c",
          weight: interactive ? 2 : 1.5,
          dashArray: interactive ? "7 6" : null,
          fillColor: "#3ec4d2",
          fillOpacity: interactive ? 0.22 : 0.08,
          interactive,
        });
        if (interactive) {
          polygon.on("click", () => zoneHandlerRef.current?.(zone.name));
          const bounds = L.latLngBounds(zone.ring);
          const label = L.marker(bounds.getCenter(), {
            interactive: false,
            keyboard: false,
            icon: L.divIcon({
              className: "zone-label",
              html: `<span>Zona disponible</span><strong>${zone.name}</strong>`,
              iconSize: [148, 38],
              iconAnchor: [74, 19],
            }),
          });
          label.addTo(zones);
        }
        polygon.addTo(zones);
      }
    }

    function paintPoints() {
      points.clearLayers();
      const visible = locations.filter(
        (record) =>
          (!focusedMunicipality || record.municipality === focusedMunicipality) &&
          (!municipality || record.municipality === municipality),
      );
      visible.forEach((record, index) => {
        if (!Number.isFinite(record.latitude) || !Number.isFinite(record.longitude))
          return;
        const marker = L.circleMarker([record.latitude, record.longitude], {
          radius: 4,
          color: "#098c9e",
          weight: 1,
          fillColor: "#5bcad5",
          fillOpacity: 0.75,
          className: reduce ? "" : "locality-point",
        });
        const text = document.createElement("span");
        text.textContent = `${record.locality} · ${record.municipality} · ${record.id}`;
        marker.bindTooltip(text, { direction: "top" });
        marker.on("click", () => handlerRef.current?.(record));
        marker.addTo(points);
        const path = marker.getElement?.() || marker._path;
        if (path && !reduce)
          path.style.animationDelay = `${Math.min(index, 28) * 16}ms`;
      });
    }

    if (!focusedMunicipality) {
      paintZones(true);
      points.clearLayers();
      if (seenFocus.current) {
        if (reduce) map.setView(OVERVIEW, 10, { animate: false });
        else map.flyTo(OVERVIEW, 10, { duration: 0.7 });
      }
      return () => {
        cancelled = true;
      };
    }

    seenFocus.current = true;
    paintZones(false);
    points.clearLayers();
    if (pins.length) {
      paintPoints();
      return undefined;
    }
    const zone = territory.find((item) => item.name === focusedMunicipality);
    if (!zone) {
      paintPoints();
      return undefined;
    }
    const reveal = () => {
      if (!cancelled) paintPoints();
    };
    if (reduce) {
      map.fitBounds(zone.ring, { padding: [56, 56], maxZoom: 12, animate: false });
      reveal();
      return undefined;
    }
    map.once("moveend", reveal);
    map.flyToBounds(zone.ring, {
      padding: [56, 56],
      maxZoom: 12,
      duration: 0.85,
    });
    return () => {
      cancelled = true;
      map.off("moveend", reveal);
    };
  }, [
    locations,
    municipality,
    focusedMunicipality,
    mini,
    selectedA,
    selectedB,
  ]);

  useEffect(() => {
    const group = pointsRef.current;
    if (!group || !mini) return;
    group.clearLayers();
    locations.forEach((record) => {
      if (!Number.isFinite(record.latitude) || !Number.isFinite(record.longitude))
        return;
      L.circleMarker([record.latitude, record.longitude], {
        radius: 5,
        color: "#098c9e",
        weight: 1,
        fillColor: "#5bcad5",
        fillOpacity: 0.75,
        interactive: false,
      }).addTo(group);
    });
  }, [locations, mini]);

  useEffect(() => {
    const group = selectionRef.current,
      map = mapRef.current;
    if (!group || !map) return;
    group.clearLayers();
    const records = [
      [selectedA, "A"],
      [selectedB, "B"],
    ].filter(([r]) => r);
    for (const [r, label] of records) {
      const marker = L.marker([r.latitude, r.longitude], {
        zIndexOffset: 1000,
        icon: L.divIcon({
          className: "selected-map-marker",
          html: `<span class="map-pin pin-${label.toLowerCase()}">${label}</span>`,
          iconSize: [36, 44],
          iconAnchor: [18, 43],
        }),
      }).addTo(group);
      const tooltip = document.createElement("strong");
      tooltip.textContent = `${label} · ${r.locality}`;
      marker.bindTooltip(tooltip, {
        permanent: true,
        direction: "bottom",
        offset: [0, 3],
        className: "selection-tooltip",
      });
    }
    if (records.length === 2)
      map.fitBounds(
        records.map(([r]) => [r.latitude, r.longitude]),
        { padding: [65, 65], maxZoom: 12, animate: false },
      );
    else if (records.length === 1)
      map.setView([records[0][0].latitude, records[0][0].longitude], 12, {
        animate: false,
      });
  }, [selectedA, selectedB]);

  function toggleTiles() {
    const map = mapRef.current,
      tiles = tileRef.current;
    if (!map || !tiles) return;
    if (map.hasLayer(tiles)) {
      map.removeLayer(tiles);
      setTilesEnabled(false);
      stopLoadingRef.current?.();
      baseReadyRef.current = false;
    } else {
      baseReadyRef.current = false;
      setMapLoading(true);
      setOffline(false);
      tiles.addTo(map);
      setTilesEnabled(true);
    }
  }

  return (
    <div className={`territory-map ${mini ? "mini-map" : ""}`}>
      <div
        ref={container}
        className="leaflet-host"
        role="region"
        aria-label="Mapa de referencia de localidades de Irapuato y Celaya"
        aria-busy={mapLoading && tilesEnabled && !offline}
      />
      {!mini && (
        <>
          {mapLoading && tilesEnabled && !offline && (
            <GeoPulse variant="map" title="Cargando mapa de referencia…" detail="Cartografía base · OpenStreetMap" delay={450} />
          )}
          <div className="map-top-label">
            <span className="map-status-dot" />
            {focusedMunicipality
              ? `LOCALIDADES · ${focusedMunicipality.toUpperCase()}`
              : "ZONAS DISPONIBLES"}
          </div>
          <div className="map-tools">
            <span className="north">
              <Compass size={20} />
              <small>N</small>
            </span>
            <button
              className="icon-button"
              aria-label="Ver ambas ciudades"
              title="Ver ambas ciudades"
              onClick={() => onChooseZone?.(null)}
            >
              <LocateFixed size={19} />
            </button>
            <button
              className="icon-button"
              aria-label={
                tilesEnabled ? "Ocultar mapa base" : "Mostrar mapa base"
              }
              title="Alternar mapa base"
              aria-pressed={tilesEnabled}
              onClick={toggleTiles}
            >
              <Layers size={19} />
            </button>
          </div>
          {(offline || !tilesEnabled) && (
            <div className="map-note">
              {offline
                ? "Sin mapa base. El catálogo y la selección siguen disponibles."
                : "Mapa base oculto. El catálogo y la selección siguen disponibles."}
            </div>
          )}
        </>
      )}
    </div>
  );
}

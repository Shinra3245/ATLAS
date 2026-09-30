import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Compass, LocateFixed, Layers } from "lucide-react";

export function TerritoryMap({
  locations = [],
  selectedA,
  selectedB,
  onSelect,
  municipality,
  mini = false,
}) {
  const container = useRef(null);
  const mapRef = useRef(null);
  const pointsRef = useRef(null);
  const selectionRef = useRef(null);
  const handlerRef = useRef(onSelect);
  const [offline, setOffline] = useState(false);
  const [tilesEnabled, setTilesEnabled] = useState(true);
  const tileRef = useRef(null);
  handlerRef.current = onSelect;

  useEffect(() => {
    const map = L.map(container.current, {
      zoomControl: !mini,
      scrollWheelZoom: !mini,
      dragging: !mini,
      doubleClickZoom: !mini,
      keyboard: !mini,
      touchZoom: !mini,
      attributionControl: true,
    }).setView([20.62, -101.06], mini ? 9 : 10);
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
    tiles.on("tileerror", () => {
      failures++;
      if (failures >= 3) {
        setOffline(true);
        if (map.hasLayer(tiles)) map.removeLayer(tiles);
      }
    });
    tiles.on("tileload", () => {
      setOffline(false);
    });
    tiles.addTo(map);
    tileRef.current = tiles;
    pointsRef.current = L.layerGroup().addTo(map);
    selectionRef.current = L.layerGroup().addTo(map);
    const observer = new ResizeObserver(() =>
      map.invalidateSize({ animate: false }),
    );
    observer.observe(container.current);
    return () => {
      observer.disconnect();
      map.remove();
      mapRef.current = null;
    };
  }, [mini]);

  useEffect(() => {
    const group = pointsRef.current;
    if (!group) return;
    group.clearLayers();
    locations
      .filter((r) => !municipality || r.municipality === municipality)
      .forEach((r) => {
        if (!Number.isFinite(r.latitude) || !Number.isFinite(r.longitude))
          return;
        const marker = L.circleMarker([r.latitude, r.longitude], {
          radius: mini ? 5 : 4,
          color: "#098c9e",
          weight: 1,
          fillColor: "#5bcad5",
          fillOpacity: 0.75,
          interactive: !mini,
        });
        const text = document.createElement("span");
        text.textContent = `${r.locality} · ${r.municipality} · ${r.id}`;
        if (!mini) marker.bindTooltip(text, { direction: "top" });
        marker.on("click", () => handlerRef.current?.(r));
        marker.addTo(group);
      });
  }, [locations, municipality, mini]);

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
    } else {
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
      />
      {!mini && (
        <>
          <div className="map-top-label">
            <span className="map-status-dot" />
            LOCALIDADES DEL MVP
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
              onClick={() => mapRef.current?.setView([20.62, -101.06], 10)}
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
          <div className="map-note">
            {offline
              ? "Sin mapa base. El catálogo y la selección siguen disponibles."
              : "Cartografía de referencia · no es una capa de riesgo"}
            <small>
              Coordenadas recibidas: CRS_UNKNOWN. No acredita precisión predial.
            </small>
          </div>
        </>
      )}
    </div>
  );
}

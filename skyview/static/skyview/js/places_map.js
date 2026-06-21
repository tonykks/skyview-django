document.addEventListener("DOMContentLoaded", function () {
  const dataEl = document.getElementById("places-map-data");
  const mapContainer = document.getElementById("places-map");

  if (!dataEl || !mapContainer || typeof L === "undefined") {
    return;
  }

  const DEFAULT_CENTER = [33.35, 126.53];
  const DEFAULT_ZOOM = 10;
  const places = JSON.parse(dataEl.textContent);
  const cleaned = places.filter(function (place) {
    return (
      place.name &&
      Number.isFinite(place.lat) &&
      Number.isFinite(place.lng)
    );
  });

  const map = L.map(mapContainer, { zoomControl: true }).setView(
    DEFAULT_CENTER,
    DEFAULT_ZOOM
  );

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap contributors",
  }).addTo(map);

  const bounds = L.latLngBounds([]);

  cleaned.forEach(function (place) {
    bounds.extend([place.lat, place.lng]);

    const marker = L.marker([place.lat, place.lng]).addTo(map);
    marker.bindTooltip(place.name, {
      permanent: true,
      direction: "top",
      className: "place-map-label",
    });

    const detailUrl = "/places/" + encodeURIComponent(place.slug) + "/";
    let popupHtml =
      "<b>" +
      place.name +
      '</b><br><a href="' +
      detailUrl +
      '">장소 영상 보기</a>';

    if (place.introUrl) {
      popupHtml +=
        '<br><a href="' +
        place.introUrl +
        '" target="_blank" rel="noopener">소개 페이지</a>';
    }

    marker.bindPopup(popupHtml);
  });

  if (bounds.isValid()) {
    map.fitBounds(bounds, { padding: [40, 40] });
  }
});

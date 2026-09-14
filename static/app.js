function formatElapsed(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return [h, m, s].map((v) => String(v).padStart(2, "0")).join(":");
}

async function refresh() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    for (const slot of data.slots) {
      const el = document.getElementById(`slot-${slot.id}`);
      if (!el) continue;
      el.classList.toggle("occupied", slot.occupied);
      el.querySelector(".status").textContent = slot.occupied ? "DOLU" : "BOŞ";
      el.querySelector(".timer").textContent = slot.occupied
        ? formatElapsed(slot.elapsed_seconds)
        : "-";
      el.querySelector(".distance").textContent =
        slot.distance_cm != null ? `${slot.distance_cm} cm` : "sensör yok";

      const historyList = el.querySelector(".history-list");
      historyList.innerHTML = "";
      if (slot.history_seconds.length === 0) {
        const li = document.createElement("li");
        li.textContent = "henüz kayıt yok";
        li.className = "history-empty";
        historyList.appendChild(li);
      } else {
        for (const seconds of slot.history_seconds) {
          const li = document.createElement("li");
          li.textContent = formatElapsed(seconds);
          historyList.appendChild(li);
        }
      }
    }
  } catch (err) {
    console.error("status fetch failed", err);
  }
}

refresh();
setInterval(refresh, 2000);

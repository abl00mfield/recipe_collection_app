//convert UTC time elements to user's local time
export function initLocalTimestamps() {
  const elements = document.querySelectorAll("time.utc-timestamp");
  elements.forEach((el) => {
    const utcTime = new Date(el.getAttribute("datetime"));
    const localString = utcTime.toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
    el.textContent = localString;
  });
}

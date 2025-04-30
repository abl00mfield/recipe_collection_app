document.addEventListener("DOMContentLoaded", function () {
  const messages = document.querySelectorAll(".messages li");

  messages.forEach((message) => {
    setTimeout(() => {
      message.classList.add("fade-out"); // 👈 Add the class for sliding + fading
      setTimeout(() => {
        message.remove();
      }, 1000); // wait for fade/slide animation to complete
    }, 3000); // start fade/slide after 3 seconds
  });

  // Convert UTC <time> elements to user's local time
  const elements = document.querySelectorAll("time.utc-timestamp");
  elements.forEach((el) => {
    const utcTime = new Date(el.getAttribute("datetime"));
    const localString = utcTime.toLocaleString(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    });
    el.textContent = localString;
  });
});

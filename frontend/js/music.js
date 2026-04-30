const queryForm = document.querySelector("#query-form");
const resultList = document.querySelector("#result-list");
const resultMessage = document.querySelector("#result-message");
const clearButton = document.querySelector("#clear-query");

function showQueryMessage(message, type = "info") {
  if (!resultMessage) return;

  resultMessage.textContent = message;
  resultMessage.className = `message ${type}`;
  resultMessage.hidden = !message;
}

function formToSongQuery(form) {
  const formData = new FormData(form);
  const query = {};

  for (const [key, value] of formData.entries()) {
    const trimmed = value.trim();
    if (trimmed) query[key] = trimmed;
  }

  return query;
}

function queryStringFrom(query) {
  const params = new URLSearchParams();

  Object.entries(query).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });

  return params.toString();
}

function renderResults(songs) {
  resultList.innerHTML = "";

  songs.forEach((song) => {
    resultList.appendChild(renderSongCard(song, "Subscribe", subscribeToSong));
  });
}

if (queryForm) {
  queryForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const query = formToSongQuery(queryForm);

    resultList.innerHTML = "";

    if (!Object.keys(query).length) {
      showQueryMessage("Enter at least one search field.", "error");
      return;
    }

    showQueryMessage("Searching...", "info");

    try {
      const data = await apiRequest(`/music/query?${queryStringFrom(query)}`);

      if (Array.isArray(data) && data.length) {
        renderResults(data);
        showQueryMessage(`${data.length} result${data.length === 1 ? "" : "s"} found.`, "success");
      } else {
        showQueryMessage("No result is retrieved. Please query again", "info");
      }
    } catch (error) {
      showQueryMessage(`Unable to query music: ${error.message}`, "error");
    }
  });
}

if (clearButton) {
  clearButton.addEventListener("click", () => {
    queryForm.reset();
    resultList.innerHTML = "";
    showQueryMessage("", "info");
  });
}

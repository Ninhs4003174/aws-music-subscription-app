const subscriptionList = document.querySelector("#subscription-list");
const subscriptionEmpty = document.querySelector("#subscription-empty");

function songIdFor(song) {
  return song.song_id || `${song.artist || ""}#${song.title || ""}`;
}

function artistImageFor(song) {
  return song.s3_image_url || song.image_url || song.img_url || "";
}

function normalizeSong(song) {
  const songId = song.song_id || "";
  const parts = songId.split("#");

  return {
    ...song,
    song_id: song.song_id || songIdFor(song),
    artist: song.artist || parts[0] || "Unknown artist",
    title: song.title || parts[1] || "Untitled song",
    year: song.year || "",
    album: song.album || "",
    image_url: song.image_url || song.img_url || "",
    s3_image_url: song.s3_image_url || ""
  };
}

function extractSubscriptionArray(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.subscriptions)) {
    return data.subscriptions;
  }

  if (Array.isArray(data.items)) {
    return data.items;
  }

  return [];
}

function renderSongCard(song, actionLabel, actionHandler) {
  const displaySong = normalizeSong(song);

  const article = document.createElement("article");
  article.className = "song-card";

  const imageUrl = artistImageFor(displaySong);

  if (imageUrl) {
    const image = document.createElement("img");
    image.className = "artist-image";
    image.alt = `${displaySong.artist} image`;
    image.loading = "lazy";
    image.src = imageUrl;
    article.appendChild(image);
  }

  const details = document.createElement("div");
  details.className = "song-details";

  const title = document.createElement("h3");
  title.textContent = displaySong.title;

  const artist = document.createElement("p");
  artist.className = "song-artist";
  artist.textContent = displaySong.artist;

  const meta = document.createElement("p");
  meta.className = "song-meta";
  meta.textContent = [displaySong.album, displaySong.year].filter(Boolean).join(" - ");

  const action = document.createElement("button");
  action.type = "button";
  action.className = actionLabel === "Remove" ? "button button-danger" : "button button-small";
  action.textContent = actionLabel;
  action.addEventListener("click", () => actionHandler(displaySong, action));

  details.append(title, artist, meta, action);
  article.appendChild(details);

  return article;
}

async function loadSubscriptions() {
  const user = getCurrentUser();

  if (!subscriptionList || !subscriptionEmpty) {
    return;
  }

  subscriptionList.innerHTML = "";

  if (!user) {
    subscriptionEmpty.hidden = false;
    subscriptionEmpty.textContent = "Login first to view your subscriptions.";
    return;
  }

  subscriptionEmpty.hidden = true;
  subscriptionEmpty.textContent = "No subscriptions yet.";

  try {
    const data = await apiRequest(`/subscriptions/${encodeURIComponent(user.email)}`);
    const subscriptions = extractSubscriptionArray(data);

    if (!subscriptions.length) {
      subscriptionEmpty.hidden = false;
      subscriptionEmpty.textContent = "No subscriptions yet.";
      return;
    }

    subscriptions.forEach((song) => {
      const card = renderSongCard(song, "Remove", unsubscribeFromSong);
      subscriptionList.appendChild(card);
    });
  } catch (error) {
    subscriptionEmpty.hidden = false;
    subscriptionEmpty.textContent = `Unable to load subscriptions: ${error.message}`;
  }
}

async function subscribeToSong(song, button) {
  const user = getCurrentUser();

  if (!user) {
    showQueryMessage("Please login before subscribing to music.", "error");
    return;
  }

  button.disabled = true;
  button.textContent = "Adding...";

  try {
    await apiRequest("/subscribe", {
      method: "POST",
      body: JSON.stringify({
        user_email: user.email,
        song_id: songIdFor(song)
      })
    });

    button.textContent = "Subscribed";
    await loadSubscriptions();
  } catch (error) {
    button.disabled = false;
    button.textContent = "Subscribe";
    showQueryMessage(error.message, "error");
  }
}

async function unsubscribeFromSong(song, button) {
  const user = getCurrentUser();

  if (!user) {
    return;
  }

  button.disabled = true;
  button.textContent = "Removing...";

  try {
    await apiRequest("/subscribe", {
      method: "DELETE",
      body: JSON.stringify({
        user_email: user.email,
        song_id: songIdFor(song)
      })
    });

    await loadSubscriptions();
  } catch (error) {
    button.disabled = false;
    button.textContent = "Remove";
    subscriptionEmpty.hidden = false;
    subscriptionEmpty.textContent = error.message;
  }
}

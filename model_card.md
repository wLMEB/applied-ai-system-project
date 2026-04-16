# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 suggests up to 5 songs from a small catalog based on a user's
preferred genre, mood, energy level, and acoustic preference.

- **Intended users:** Students learning how content-based recommenders work.
- **Intended context:** Classroom exploration and experimentation only — not
  designed for real streaming products or real users.
- **Non-intended use:** This system should not be used to curate playlists for
  actual music consumption because it has a tiny catalog (20 songs), no
  listening history, and no understanding of lyrics, culture, or context.

---

## 3. How the Model Works

VibeFinder looks at each song in its catalog and gives it a score based on how
well it matches what the user told us they like.

- If the song's **genre** exactly matches the user's favorite, it earns 2 points.
- If the song's **mood** exactly matches, it earns 1 point.
- The closer the song's **energy** is to the user's target (on a 0–1 scale),
  the more points it earns — up to 1.5 points for a perfect match.
- Acoustic-loving users earn a 0.5 bonus for songs that actually sound acoustic.
- The **emotional positivity (valence)** of the song is compared to the user's
  preferred vibe, awarding up to 0.5 bonus points.

After every song is scored, they are sorted from highest to lowest.  An optional
**artist-diversity penalty** (−1.0 per extra appearance of the same artist)
ensures the list does not get filled with tracks from a single artist.

Users can also switch between four **ranking modes** that shift the relative
importance of genre, mood, and energy — letting them explore how the weights
change the results.

---

## 4. Data

- **Dataset size:** 20 songs loaded from `data/songs.csv`
- **Attributes per song:** 15 — including genre, mood, energy, tempo_bpm,
  valence, danceability, acousticness, popularity, release_decade,
  instrumentalness, speechiness, and liveness
- **Genres represented:** pop, lofi, rock, ambient, synthwave, jazz, indie pop,
  hip-hop, classical, country, r&b, electronic, folk
- **Moods represented:** happy, chill, intense, moody, relaxed, focused
- **Decades represented:** 2010s and 2020s (no older music)
- **Missing representation:** No metal, reggae, blues, classical non-Western
  music, or songs from before 2010.  The dataset also skews toward Western pop
  conventions around what "happy" and "intense" mean.

---

## 5. Strengths

- **Transparent:** Every recommendation comes with a plain-language explanation
  showing exactly which features matched and how many points each earned.
- **Works well for mainstream profiles:** A "happy pop fan" or a "chill lofi
  listener" gets consistently intuitive top results because those genres and
  moods are well-represented in the catalog.
- **Artist diversity:** The built-in diversity penalty prevents any single artist
  from flooding the recommendation list — a simple but effective fairness measure.
- **Explainability:** Because the scoring is rule-based, any result can be fully
  explained without a black-box neural network.

---

## 6. Limitations and Bias

- **Genre dominance:** A genre match is worth 2 points — the highest single
  contributor. This means a pop song with the wrong mood still beats a perfect
  mood+energy match from a different genre. Users who prefer niche genres with
  only 1 representative song in the catalog (e.g., classical, country) will get
  poor recommendations because the genre bonus can never fire after song #1.

- **Pop over-representation:** 4 of 20 songs (20 %) are pop. Pop fans see many
  genre bonus opportunities; fans of folk, r&b, or classical see almost none.
  This is a dataset imbalance bias — the algorithm itself is fair, but the data
  it runs on is not.

- **No negative signals:** The system has no way to say "I *dislike* sad songs."
  It can only add points, never remove them for mismatches.  A user who hates
  intense music will still see intense songs in the list if their energy target
  is high.

- **Binary category matching:** "indie pop" and "pop" are treated as completely
  different genres even though they overlap heavily in practice.  A listener of
  one would likely enjoy the other, but the algorithm awards 0 genre points in
  that case.

- **No temporal or contextual awareness:** The system does not know whether the
  user is working out, studying, or relaxing right now.  The same profile always
  returns the same result regardless of context.

---

## 7. Evaluation

**Profiles tested:**

1. **Happy Pop Fan** (genre=pop, mood=happy, energy=0.80) — Results matched
   intuition perfectly: Sunrise City ranked #1 with a near-perfect score.

2. **Chill Lofi Listener** (genre=lofi, mood=chill, energy=0.38, acoustic=True)
   — Top 2 results were both lofi tracks. Mountain Air and Spacewalk Thoughts
   appeared correctly as acoustic cross-genre alternatives.

3. **High-Energy EDM Gym** (genre=electronic, mood=intense, energy=0.95)
   — Electric Storm dominated at #1; positions 2–3 were rock and pop songs with
   matching intensity but different genres, showing the mood/energy combo can
   partially compensate for a missing genre match.

4. **Acoustic Folk Wanderer** (genre=folk, mood=chill, energy=0.30, acoustic=True)
   — Mountain Air was the only perfect genre match; the rest of the list correctly
   skewed acoustic and low-energy despite spanning different genres.

5. **Moody Indie Night Owl** (genre=indie pop, mood=moody, energy=0.65)
   — Surprising result: Rooftop Lights (a *happy* indie pop song) ranked #1
   because genre weight alone (2 pts) outweighed mood mismatch.  This highlighted
   the limitation that genre dominates mood.

**Experiment run:** Switched from `standard` to `energy_first` mode for the Happy
Pop Fan profile.  Genre diversity immediately improved — three different genres
appeared in the top 4 instead of all pop — confirming that the genre weight is the
main homogenising force in standard mode.

**Surprise:** The same Neon Echo artist would appear twice in the Happy Pop Fan top 5
without the diversity penalty, illustrating how quickly a tiny catalog can create an
accidental "artist filter bubble."

---

## 8. Future Work

1. **Larger and more balanced dataset** — 200+ songs with equal genre distribution
   would make the system useful for more listener types and reduce the pop bias.

2. **Soft genre matching** — Define a genre-similarity matrix (e.g., "indie pop"
   is 70 % similar to "pop") so partially matching genres still earn partial points
   instead of zero.

3. **Negative preference signals** — Allow the user to specify genres or moods to
   *avoid*, and subtract points when those appear.

4. **Context-aware profiles** — Let users specify a listening context (workout,
   study, sleep) and adjust weights automatically based on that context.

5. **Collaborative layer** — Track which songs users skip or replay and update
   weights over time, turning the content-based system into a hybrid recommender.

---

## 9. Personal Reflection

Building VibeFinder showed me how much a recommendation system's "intelligence" is
really just a set of design decisions frozen into numbers.  The weight I assigned to
genre (2.0) versus mood (1.0) was a judgment call — and that single choice cascaded
into every profile I tested.  Changing it to `energy_first` mode instantly changed
the character of the recommendations without touching the data at all.

Using AI tools during this project was most useful for brainstorming scoring formulas
and quickly generating 10 additional songs with realistic attributes.  However, I had
to double-check every output: the AI generated a song with energy=1.2 (outside the 0–1
scale) and another with an invalid release decade.  It's a good reminder that AI
suggestions are a starting point, not a finished product.

What surprised me most was how easily a filter bubble forms even in a 20-song catalog.
Without the artist-diversity penalty, two Neon Echo tracks appeared in the same top 5
list.  In a real system with millions of songs, the same effect at scale would mean an
entire playlist of one artist or one tempo — exactly the kind of thing that makes a
recommendation engine feel stale over time.  Real-world fairness in AI is not just
about legal compliance; it shows up in every weight, every tie-breaker, and every
design choice about what the system optimises for.

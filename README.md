# Music Recommender Simulation

## Project Summary

This project is a content-based music recommendation simulator built in Python.
Given a user's taste profile (preferred genre, mood, energy level, and whether they
like acoustic sounds), the system scores every song in a 20-song catalog and returns
the top matches — along with a plain-language explanation for each pick.

The project mirrors how real streaming platforms like Spotify decide what to play
next, but at classroom scale so every decision can be inspected and understood.

---

## How The System Works

### Real-world recommenders (context)

Platforms like Spotify and YouTube use two main strategies:

- **Collaborative filtering** — "people who liked what you like also liked *X*."
  It mines patterns across millions of users without caring what the songs actually
  sound like.
- **Content-based filtering** — matches a song's audio features (tempo, energy,
  valence, genre) directly to what you have shown you prefer.

This simulator uses **content-based filtering** exclusively because it is
transparent and works without needing a crowd of other users.

### Algorithm Recipe

| Feature | Weight (standard mode) | How it's scored |
|---|---|---|
| Genre match | +2.0 | Binary: exact string match |
| Mood match | +1.0 | Binary: exact string match |
| Energy similarity | 0-1.5 | `(1 - |song_energy - target|) * 1.5` |
| Acousticness bonus | +0.5 | Only if user `likes_acoustic` AND song acousticness > 0.6 |
| Valence similarity | 0-0.5 | `(1 - |song_valence - target|) * 0.5` |

Maximum possible score in standard mode: **5.5 points**

Songs are then ranked highest-to-lowest.  An optional **artist-diversity penalty**
subtracts 1.0 from each additional appearance of the same artist so no single
artist dominates the list.

### Four Ranking Modes (stretch feature)

| Mode | Genre wt | Mood wt | Energy wt |
|---|---|---|---|
| `standard` | 2.0 | 1.0 | 1.5 |
| `genre_first` | 4.0 | 0.5 | 0.5 |
| `mood_first` | 1.0 | 3.0 | 0.5 |
| `energy_first` | 0.5 | 0.5 | 3.0 |

### Song features used

`genre`, `mood`, `energy`, `valence`, `danceability`, `acousticness`,
`tempo_bpm`, `popularity`, `release_decade`, `instrumentalness`,
`speechiness`, `liveness`

### UserProfile fields

`favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`,
`target_valence`, `preferred_decade`

---

## Getting Started

### Setup

```bash
python -m venv .venv
# Mac/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

pip install -r requirements.txt
```

### Run the recommender

```bash
python -m src.main
```

### Run tests

```bash
pytest
```

---

## Terminal Output Screenshots

![All 5 profile recommendations](All_profile.png)

### Profile 1 — Happy Pop Fan

**Comment:** Sunrise City is the clear winner — it matches genre, mood, AND energy.
Gym Hero ranks 2nd because it matches genre and energy, but misses on mood (intense vs happy).
The diversity penalty knocks Neon Afterglow (also by Neon Echo) down from #3 to #5.

### Profile 2 — Chill Lofi Listener

**Comment:** Both lofi songs (Library Rain and Midnight Coding) score almost identically
because they are near-perfect matches. The system correctly catches Mountain Air and
Spacewalk Thoughts as secondary chill/acoustic alternatives even though they are different
genres, showing that the energy+acoustic features provide genre diversity.

### Profile 3 — High-Energy EDM Gym

**Comment:** The EDM profile correctly surfaces Electric Storm at #1 (genre + mood + energy
triple match). Ranks 2 and 3 miss genre but nail mood and energy. This shows the genre
weight pulls Electric Storm far ahead of similarly energetic songs.

### Profile 4 — Acoustic Folk Wanderer

**Comment:** Mountain Air is the obvious winner (the only folk song). Positions 2-5 are all
correctly low-energy and acoustic, even though they span different genres. This profile
demonstrates that the acoustic weight successfully crosses genre boundaries.

### Profile 5 — Moody Indie Night Owl

**Comment:** Interesting behavior here — Rooftop Lights wins on genre match even though its
mood (happy) is the opposite of what the user wants (moody). The system cannot tell that a
"happy indie pop" song would feel wrong for someone wanting "moody indie pop." This is a
clear weakness: mood mismatch does not penalize; it just fails to add points.

---

## Experiments You Tried

### Experiment 1 — Standard vs Energy-First mode for Happy Pop Fan

**Question:** What happens when energy similarity is worth 3× as much as genre?

**Result:** In `standard` mode, genre dominates — three pop songs fill the top 3.
In `energy_first` mode, genre and mood weights shrink to 0.5 each, so Summer Bounce
(indie pop, happy, energy=0.80) jumps to #2 ahead of Gym Hero, and country song
Boot Scootin enters the top 4. The list becomes more genre-diverse when energy is
the primary signal.

**Takeaway:** Genre is the strongest default predictor because it is worth 2 points for
a binary match. Reducing its weight immediately diversifies results.

### Experiment 2 — Artist Diversity Penalty

Turned off diversity (`diversity=False`) for the Happy Pop Fan profile.
Without the penalty, Neon Echo occupies both #1 (Sunrise City) and #3 (Neon Afterglow),
creating a mini filter bubble around a single artist.
With the penalty enabled, Neon Afterglow drops from #3 to #5, letting Summer Bounce
and Boot Scootin appear — a more varied listening experience.

### Experiment 3 — Chill Lofi vs Acoustic Folk

Both profiles prefer low-energy, acoustic music, but the lofi profile gets exclusively
lofi/ambient songs while the folk profile correctly leads with Mountain Air.
This shows the genre weight (2.0) is the decisive differentiator between two otherwise
similar taste profiles.

---

## Limitations and Risks

- **Small catalog** — 20 songs is not enough to provide real variety; several profiles
  hit the same 5 songs from different angles.
- **No lyric or language awareness** — two songs can sound identical to the algorithm
  even if one is in English and one in Mandarin.
- **Pop over-representation** — 4 of 20 songs are pop, so pop fans get many near-matches
  while niche genres (classical, country) have only 1 song each.
- **Binary genre/mood matching** — "indie rock" and "rock" are treated as completely
  different even though they overlap heavily in real listener taste.
- **No listening history** — the system treats every session as a fresh start with no
  memory of what the user has already heard.

---

## Reflection

See [model_card.md](model_card.md) for a full model card and personal reflection.

Real recommenders feel magical because they combine content signals with millions of
behavioral data points from other listeners. This simulation shows that even a simple
scoring formula can produce reasonable results — and reveals exactly where judgment
calls (what to weight, how to handle ties, when to inject diversity) translate directly
into whose taste gets served well and whose gets ignored.

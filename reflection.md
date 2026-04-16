# Reflection: Profile Comparison Notes

## Happy Pop Fan vs. Chill Lofi Listener

The Happy Pop Fan and Chill Lofi Listener are almost mirror images of each other.
The pop fan targets high energy (0.80) and happiness; the lofi listener targets low
energy (0.38) and chill vibes.  Their top songs share zero overlap in the results,
which makes intuitive sense — you would not play "Sunrise City" (upbeat 118 BPM pop)
for someone who just wants to study with "Library Rain" in the background.

The interesting thing is *why* they differ: it is not just genre.  The energy
similarity score completely reverses — songs that score 1.47 energy points for the
pop fan score near-zero for the lofi listener, and vice versa.  Energy is therefore
the most powerful continuous differentiator between these two profiles.

## High-Energy EDM Gym vs. Acoustic Folk Wanderer

These two profiles share almost nothing in their top lists.  The EDM profile needs
intense, loud, fast — it surfaces Electric Storm, Storm Runner, Gym Hero, and
Basement Beats.  The Folk Wanderer wants quiet, acoustic, low-energy — it surfaces
Mountain Air, Spacewalk Thoughts, Library Rain, Midnight Coding.

What changed and why it makes sense: the acousticness feature adds 0.5 bonus points
only for the folk profile (because `likes_acoustic=True`).  Without that flag, the
folk wanderer's top 5 would still be acoustic songs (because their energy profile
matches), but the system would not know *why*.  The explicit acoustic flag is a rare
example of a binary preference beating a continuous one — it acts as a filter that
amplifies songs the energy/mood signals already preferred.

## Happy Pop Fan vs. Moody Indie Night Owl

Both profiles have similar energy targets (~0.65–0.80) but opposite moods and
adjacent genres (pop vs. indie pop).  The pop fan's top 5 is entirely pop/indie-pop
and happy; the moody night owl's top 5 blends indie pop and moody tracks.

The surprising result: Rooftop Lights (a *happy* indie pop song) tops the night owl
list because its genre match (indie pop = 2.0 points) outweighs the missing mood
match.  This reveals the core tension in the algorithm: genre is worth twice as much
as mood.  A real listener who specifically wants "moody" music would find this
frustrating — they asked for atmosphere, but the system gave them genre loyalty
instead.  This is the kind of bias that is invisible until you test edge cases.

## Standard Mode vs. Energy-First Mode (Happy Pop Fan)

Running the same Happy Pop Fan profile in `energy_first` mode (genre weight halved to
0.5, energy weight doubled to 3.0) changed the top 5 noticeably.  In standard mode,
three of the top 5 are pop songs.  In energy_first mode, only one pop song appears in
the top 5, replaced by indie pop and country tracks that happen to sit at energy~0.70-0.80.

This experiment shows that the *genre filter bubble* is largely a product of the
genre weight being the highest single value.  When you reduce it, the system becomes
more genre-diverse — but it also stops feeling like a "pop recommender" and becomes
more of a "high-energy recommender."  Neither is wrong; they answer different questions
about what the user wants.

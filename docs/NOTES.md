## Open questions
- How can we define physiological synchrony? (or interactional synchrony?)
- When can it be said of a group of individuals that they have physiological coherence?
- Can we determine coherence by just using electrophysiology or do we need more information?
- What can we do with electrophysiology alone?
- What can be said of a group of people in which certain characteristics are synchronous?
- What is the relationship between empathy and interactional synchrony?
- What is the relationship between movement and interactional synchrony?
- How long does synchrony have to last to consider it a "locking" event?
- What is known of psychological states and their effect in physiological metrics? How can we better understand the impact of an experience when all we have is electrophysiology?
- All biosignals are cyclical, different people have differences in rate and phase that are natural. Obviously they will synch up in the same way that fireflies synch up. When can we safely assume by just looking at data that we are looking at an event of psychophysical significance rather than just natural synchrony of the kind one would expect in a sea of waves?
 
## Engineering problems
- Mobility: Nexus vs. HOLST necklace (only brands experienced)
- Wireless protocols: Bluetooth is the devil. Range is important. Do I need to be near the base station? Or can I be anywhere in a hospital-sized building?
- Device clock synchronization - it is essential for these kinds of studies that devices synch up to a single clock and that logs from all devices match up when visualized next to each other.
- Synchronization of video/audio/light actuation to events in the log timeseries.
- Timeseries tagging (and side by side visualization with audio/video/light)

## Signal analysis
- EDF format compatibility is incredibly useful (HOLST necklace doesn't support it)
- Phase and Frequency domain analysis good candidates to yield clues on synchrony.
- Some signals seem better suited for frequency analysis such as HR, others would seem to be better suited for phase, such as RESP.
- Detection of phase-locking and frequency-locking as discrete events.
- Coherence ratios: can we obtain a quantitative measure of "how much this individual is from this individual" at this particular time?
#### Offline
EDF browser is great but fairly limited when doing postprocessing (e.g. comparative PSR)
#### Realtime
- Locking events and real-time coherence ratios would be useful to modulate behaviour of actuators.

## Experimental protocol
- Very important to mark beginning and end of experiment in the timeseries log.
  - Nexus has a button that appears as a SWITCH feed in the timeseries log. (but when battery depletion causes the switch LED to blink the timeseries recording reflects this... confusing)
  - HOLST relies on external operator doing the timeseries tagging.
- Experiments involving deprivation (of light or sound for example) must be rigorous, avoid leaks.

## Performative protocol
Most performative systems work with discrete absolute ranges. Protocols such as DMX, MIDI, etc. To solve this, most processing applications work in discrete ranges too. This means that relative signals are of limitted use use and clipping them is not sufficient, as there will be significant data loss. Respiration is an example, a real-time adaptive rangefinder algorithm is very handy for actuation.

TCP is badly suited for real-time applications, UDP is better when ocassional packet loss is acceptable.

Bluetooth is the devil, nobody uses Bluetooth on stage.
 
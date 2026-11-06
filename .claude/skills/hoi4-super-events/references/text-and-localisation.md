# HOI4 Super-Events: Text and localisation

Part of the [hoi4-super-events](../SKILL.md) skill. Read before writing or editing a super-event's localisation keys, title, description or button text.

## 5. Localisation format

Super-event localisation must follow the existing repository format.

Example:

```yaml
example_super_event.1.t: "Undead?"
example_super_event.1.d: "The dead have risen, spreading terror and confusion.\n\nWitnesses describe scenes of horror as reanimated corpses or \"zombies\" began to terrorize cities and rural areas alike. The outbreak's cause appears to be unknown.\n\nAuthorities are urging the public to remain vigilant and avoid contact with anyone exhibiting unusual behavior."
example_super_event.1.a: "Do you like to take a yo-yo for a ride?" # Ironic remark
example_super_event.1.q: "This, then, is how you should pray: 'Our Father in heaven, hallowed be your name.' \n §Y-Matthew 6:9-§!" # An actual quote that fits the situation
```

Required keys:

- `.t` for title
- `.d` for description
- `.a` for button text
- `.q` for quote

Keep the key numbering aligned with the actual super-event slot.

Do not invent a different localisation pattern unless the existing repo pattern has changed.

## 6. Title rules

A good super-event title should be short, memorable, and specific.

It can be:

- direct
- ironic
- ominous
- religious
- political
- military
- bureaucratic
- poetic
- understated

Avoid generic titles such as:

- The End Begins
- World in Flames
- The Final Crisis
- Humanity Falls
- Darkness Rises

Use titles that fit the event's actual identity.

## 7. Description rules

The description should explain the event clearly without turning into a normal event wall of text.

It should:

- give the player enough context
- fit the tone of the event
- avoid overexplaining mechanics
- avoid direct spoilers if the event is meant to remain uncertain
- describe visible consequences or public understanding
- keep uncertainty where the event has not fully revealed itself

For secret or uncertain events, use partial information:

- observers are unsure
- reports conflict
- foreign diplomats avoid clear statements
- intelligence agencies disagree
- governments deny involvement
- regional witnesses give different accounts
- the full meaning is not yet clear

Do not reveal a hidden world-ending branch too early.

## 8. Button text and remark rules

The button text (`.a`) should feel like a reaction to the moment.

It may be:

- ironic
- grim
- understated
- religious
- ideological
- military
- sarcastic
- resigned
- coldly bureaucratic
- a meaningful cultural reference

Button text can use a short cultural reference when it fits the super-event.

Possible sources include:

- songs
- films
- books
- poems
- games
- political slogans
- religious texts
- historical remarks
- internet-era phrases only when the event intentionally fits that tone

Examples of the kind of source that may be considered include Steely Dan lyrics, a line from *The Lord of the Rings*, a film line, or a book line, but only if the reference genuinely fits the event.

Use the repository web research workflow from `AGENTS.md` to verify the exact wording and source of any referenced line.

For modern copyrighted songs, films, books, or games, keep the line very short. Prefer a short fragment, a title-like reference, or a paraphrased allusion when a direct quote would be too long.

Avoid generic button text such as:

- OK
- We must act
- This is terrible
- The world will never be the same

The button text should be short enough to fit well in-game.

Document the cultural source in the super-event research note when the button text is a reference.


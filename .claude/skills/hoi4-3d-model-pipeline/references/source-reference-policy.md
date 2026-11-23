# Model Reference Source Policy

Read and apply this policy before searching for or approving a 3D model reference.

Every model reference is made from existing references and research, never from a text prompt alone (D-110). Which references fit depends on the subject: a real subject follows real references, and a fantasy subject follows designed art.

## Real subjects

A real subject is something that existed: a tank, a ship, a plane, a gun, a uniform, a vehicle or a building style. Research finds its real references, such as photographs, plans and drawings, museum pieces and period art, and the picture follows them. A ship or plane made for a mod always starts from such references (D-111).

Use only public-domain or openly licensed references, for example a government photograph, a museum's open-access image or a Creative Commons file. These may be given to the image generator as input. Record each one in the card's Sources row and the job's `reference_sources` with its source page, licence and SHA-256, and archive its bytes unchanged under `refs/source/`. Do not use a reference whose licence is unclear, or one marked `NoAI` or the like.

## Fantasy subjects

A fantasy subject (a creature, a fantasy people, an invented machine) follows designed art. Its own reference comes first: the owner's drawings or the mod's existing art. The owner's drawings never leave the mod's private folder (D-123). They are never uploaded to an online service, and the 3D-ready picture is made from them offline or by the mod's own image lane, so only that picture goes online.

When a fantasy subject has no reference of its own, search for modern designed artwork: game concept art, game character or unit art, game production or promotional art, tabletop or miniature concepts and renders, fantasy or horror illustration, and professional character or creature design sheets. Historical photographs, museum works and period art do not set a fantasy subject's look. For a real detail it carries, such as a period weapon or armour, they may serve as references for that detail under the rules for real subjects.

## Records

Prefer official artist, game studio, publisher, portfolio, museum, archive or asset pages. Record the source and direct URLs, title, creator or publisher, retrieval date, original dimensions and format, SHA-256, rights or licence, reuse status, user authorization, and every explicit AI-use restriction. Archive selected original bytes unchanged as `refs/source/untouched.<ext>` and preserve the record in `refs/source/provenance.json`. A copyrighted source may be classified `reference_only_user_authorized` only when the user explicitly directs the project to use that actual game or artwork reference. An explicit `NoAI` or equivalent restriction still disqualifies it.

When no authoritative user-supplied source exists, document the Internet search scope, queries, date, eligible candidate URLs, rights decisions, and exact rejection reasons in `refs/source/source_search.md`. A generic result, a reference that fails the rules for its kind of subject, or an unusable copyrighted candidate is not proof that the eligible search failed.

## The model-ready picture

For licensed or explicitly user-authorized sources, use the image generator to create one model-ready picture informed by them. For a real subject the picture keeps the real thing's shape, proportions and markings. For a fantasy subject it is a substantially original refinement that keeps the selected traits and the intended unit identity. Either may clarify or complete model readability and adapt pose, composition, silhouette, background, or other production-facing presentation. It need not be pixel-faithful. Reject a source that cannot support a defensible picture without losing the subject's identity.

Keep the untouched sources, the model-ready picture, its prompt, the processing record, source-to-picture checksums, and the comparison as separate evidence surfaces. Obtain explicit parent or user approval of the comparison before the first paid generation. Each geometry task receives exactly one approved clean input image: a weapon-free body input and a separate input for each required weapon. Source pages, untouched sources, sheets, collages, turnarounds, contact sheets, comparisons, and diagnostic views remain evidence only. If alpha is required, request native transparent output. A checkerboard or painted transparency is not an alpha channel.

Creating a source-free reference is allowed only after a reasonable documented search finds no suitable source and the parent or user explicitly requests that specific fallback. Ordinary approval to create the 3D model authorizes the source-informed route, not a source-free replacement design. Record the fallback approval, prompt, model or route, output checksum, and restrictions.

Keep source, adapted input, provider output, Blender checkpoint, and runtime derivative distinct. Record checksums and lineage for every transition and never overwrite the original.

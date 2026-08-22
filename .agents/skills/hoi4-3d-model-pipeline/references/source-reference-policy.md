# Model Reference Source Policy

Read and apply this policy before searching for or approving a 3D model reference.

The selected model reference must be modern designed artwork. Prioritize game concept art, game character or unit art, game production or promotional art, tabletop or miniature concepts or renders, fantasy or horror illustration, and professional character or creature design sheets.

Archival photographs, museum works, historical paintings or drawings, historical plates, antiquities, archaeological images, ethnographic records, reenactment photography, and documentary imagery cannot satisfy the source gate. Do not collect them as model-reference candidates, place them on the shortlist, include them in model comparison sheets, or hand them off as selected references.

Excluded material may be consulted only as separately labelled background context when genuinely necessary. Its pixels must never enter ImageGen, Meshy, a model-reference adaptation, or a source comparison presented for model approval.

Prefer official artist, game studio, publisher, portfolio, or asset pages. Record the source and direct URLs, title, creator or publisher, retrieval date, original dimensions and format, SHA-256, rights or license, reuse status, user authorization, and every explicit AI-use restriction. Archive selected original bytes unchanged as `refs/source/untouched.<ext>` and preserve the record in `refs/source/provenance.json`. A copyrighted source may be classified `reference_only_user_authorized` only when the user explicitly directs the project to use that actual game or artwork reference; an explicit `NoAI` or equivalent restriction still disqualifies it.

When no authoritative user-supplied source exists, document the Internet search scope, queries, date, eligible candidate URLs, rights decisions, and exact rejection reasons in `refs/source/source_search.md`. A generic result, excluded historical material, or an unusable copyrighted candidate is not proof that the eligible search failed.

For licensed or explicitly user-authorized source artwork, use ImageGen only in faithful edit mode to improve resolution, isolate the subject, create genuine transparency, remove scenery, a display base, extra figures, or irrelevant text, repair alpha edges, and clean compression, exposure, contrast, or colour defects. Preserve the exact subject identity, silhouette, pose, anatomy, clothing, armour, weapons, proportions, materials, palette, and distinctive details. Do not restyle, replace, complete, or substantially redesign it. Reject a source with essential cropped, obscured, missing, or unusable anatomy or equipment rather than inventing it.

Keep the untouched source, faithful edited input, edit prompt, processing record, source-to-derivative checksums, and a visual-fidelity comparison as separate evidence surfaces. Obtain explicit parent or user approval of the comparison before the Meshy call. Meshy receives exactly one approved clean input image; source pages, untouched sources, sheets, collages, turnarounds, contact sheets, comparisons, and diagnostic views remain evidence only. If alpha is required, request native transparent output; a checkerboard or painted transparency is not an alpha channel.

Creating a reference from scratch or generatively redesigning a sourced reference is allowed only after a reasonable documented search across the eligible artwork families finds no suitable source and the parent or user explicitly requests that specific fallback. Ordinary approval to create the 3D model authorizes faithful source cleanup, not replacement design. Record the fallback approval, prompt, model or route, output checksum, and restrictions.

Keep source, adapted input, provider output, Blender checkpoint, and runtime derivative distinct. Record checksums and lineage for every transition and never overwrite the original.

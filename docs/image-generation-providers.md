# Image generation providers

**Checked 2026-10-12.** Provider features, model names, access, prices, and limits change. The links below point to vendor documentation or to the named source package. A value marked “not published” means the checked vendor documentation did not provide a dependable limit or price.

## How to read this guide

The app registers image tools for each selected coding client. OpenCode uses the
project's root `opencode.json` and its `mcp` settings, following the
[OpenCode MCP server guide](https://opencode.ai/docs/mcp-servers/).

An image provider is separate from the coding environment. Pick one primary image route and add optional routes only when the workflow needs them. A route may be a local MCP server, a vendor-hosted MCP server, a direct API adapter, a local image server, or manual art.

Some services allow several images in one request. The HOI4 asset workflow should still request **one finished asset per call**. That gives each icon, portrait, or illustration its own output path and review result. Model-specific limits below are not interchangeable; check the selected model’s live schema before sending a request.

Provider sections describe the service. A note marked **Setup route** describes what the current HOI4 Mod Setup adapter actually passes through; it may support fewer models or inputs than the whole service.

Keep API keys in Windows Credential Manager or macOS Keychain. Inject a key into a local server only when it starts. Use the vendor sign-in flow for hosted MCP services. Never write keys or access tokens into project files, generated instructions, or install locks.

## Subscription and account routes

### ChatGPT subscription through GPTImage

- **Route and sign-in:** The installed [GPTImage source repository](https://github.com/Connected-Mate/gptimage) is the source for this local MCP and CLI. The user signs in through a browser with their ChatGPT account; no API key is needed. The current source can read GPTImage or Codex local auth state and calls an undocumented ChatGPT/Codex endpoint. This is an independent, unofficial integration; OpenAI does not publish or support this subscription endpoint.
- **Cost and model:** No separate API image charge. Generation uses the account’s ChatGPT usage limits, which can change or run out. The checked source defaults to a configurable GPT-5.5 route that calls the image-generation tool; do not promise a particular underlying image model.
- **References, editing, and alpha:** The MCP accepts reference-image paths and saves PNG. It has one generation tool and no separate edit-session tool. Its current tool schema has no transparent-background setting, so treat output as opaque unless the saved pixels prove otherwise.
- **Limits:** The tool describes requested output sizes with edges up to 3,840 pixels, dimensions divisible by 16, and a ratio no wider than 3:1. The source does not document the maximum reference-image count or input size.

### Codex native ImageGen

- **Route and sign-in:** When the chosen coding environment is Codex, use its built-in image generation tool. This is not an MCP server and needs no API key; sign in to Codex with the user’s ChatGPT account.
- **Cost and model:** Uses the available Codex plan allowance and usage limits. The built-in tool manages model selection; it is not a pinned API model. The separate command-line API fallback needs an OpenAI API key and should be shown as a different route.
- **References, editing, and alpha:** The built-in tool supports generation, edits, and reference images. Its current source accepts up to five reference paths and has a transparent-background flag. A Codex issue reports transparency can fail when references are included; inspect the actual file’s alpha channel before treating it as a cutout.
- **Limits:** The public built-in tool schema does not state a reliable maximum output size. The API fallback has its own separate sizes, models, key, and price.

Sources: [GPTImage source and README](https://github.com/Connected-Mate/gptimage) · [Codex image tool](https://github.com/openai/codex/blob/main/codex-rs/ext/image-generation/src/tool.rs) · [Codex image skill](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/imagegen/SKILL.md) · [Codex plan access](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan) · [transparency issue with references](https://github.com/openai/codex/issues/42743)

## API routes and hosted MCP services

### OpenAI Images API

- **Route and sign-in:** Official Images API and Responses API; authenticate with an OpenAI API key. Organization verification may be required. OpenAI does not publish a dedicated image-generation MCP server. Use the app’s own reviewed adapter to the official API; community MCP packages are not OpenAI-supported.
- **Models and cost:** Current models include GPT Image 2.5 Sunburst and Flare, GPT Image 2, 1.5, 1, and 1 Mini. Billing is by image and text tokens. As a rough 1K reference, GPT Image 2 examples range from about $0.006 at low quality to $0.211 at high; GPT Image 1.5 examples range from about $0.009 to $0.133. GPT Image 2.5 uses token-based rates, so actual cost depends on image size, quality, prompt, and references.
- **References, editing, and alpha:** Generation and edits are supported. GPT Image 2.5 supports transparent backgrounds; set a PNG or WebP output. GPT Image 2 transparency remains in preview. The API permits up to ten outputs in a request; the app should call once per asset.
- **Limits:** For GPT Image 2 and 2.5, dimensions must satisfy the model’s pixel limits; documented bounds include a 3,840-pixel maximum edge, dimensions divisible by 16, and a ratio no wider than 3:1. Image input cost is separate. The checked image API page does not give one universal reference-image count for every model.

Sources: [image generation guide and cost examples](https://developers.openai.com/api/docs/guides/image-generation/) · [create-image API reference](https://developers.openai.com/api/reference/resources/images/methods/generate) · [official CLI image-generation fallback](https://developers.openai.com/api/docs/libraries/openai-cli)

### Google Gemini and Nano Banana

- **Route and sign-in:** Use the Gemini API through Google AI Studio with an API key. Vertex AI is another cloud route using Google Cloud credentials. No first-party image-generation MCP was found; the official route is the API. Community MCP packages exist, including [gemini-mcp](https://github.com/chrischall/gemini-mcp).
- **Models and cost:** Current image models are Nano Banana 2.1, Gemini 3.1 Flash Image, Gemini 3.1 Flash Lite Image, and Nano Banana Pro (Gemini 3 Pro Image). Approximate output prices are $0.034–$0.113 for Nano Banana 2.1, $0.067–$0.151 for Flash Image, and $0.134–$0.24 for Pro, by output size. The named image models do not show a free tier in the current pricing table; batch pricing can be lower.
- **References, editing, and alpha:** Conversational editing is supported. Reference limits vary: Lite supports up to 14 references; Nano Banana 2 supports up to 10 object references and up to 4 character references; Pro supports up to 6 object, 5 character, and 3 style references. The image API docs do not document a native alpha-output option. Use a background-removal step and verify the result.
- **Limits:** Image outputs run from 512 pixels on selected models through 4K. Aspect ratios and supported reference types differ by model. Google adds a SynthID watermark to generated images.

Sources: [image generation and model guide](https://ai.google.dev/gemini-api/docs/image-generation) · [pricing](https://ai.google.dev/gemini-api/docs/pricing) · [Gemini API MCP client support](https://github.com/google-gemini/gemini-cli/blob/main/docs/tools/mcp-server.md)

### fal.ai

- **Route and sign-in:** fal’s official hosted MCP is available at https://mcp.fal.ai/mcp and uses a fal API key. fal also documents a browser sign-in relay for supported clients. No local provider package is needed for the hosted route.
- **Models and cost:** fal exposes a changing catalog that includes FLUX, Recraft, Ideogram, Seedream, Nano Banana, and other partner models. Billing is per image or per megapixel, depending on the model. Current examples include FLUX.1 Dev at about $0.025 per megapixel, Recraft V3 raster at about $0.04 per image, and Nano Banana 2 at about $0.08 per image.
- **References, editing, and alpha:** Capabilities depend on the selected endpoint. fal hosts image-edit routes and native transparent-output endpoints such as Ideogram Transparent. Many other models need a separate background-removal operation.
- **Limits:** Each endpoint publishes its own image count, reference count, format, and dimensions. Do not apply one model’s limits to the whole fal catalog.

Sources: [fal MCP announcement](https://blog.fal.ai/connect-your-ai-to-1-000-models-with-the-fal-mcp-server/) · [current pricing](https://fal.ai/pricing) · [image-model catalog](https://fal.ai/explore/best-ai-image-generators) · [Ideogram transparent endpoint example](https://fal.ai/models/fal-ai/ideogram/v3/generate-transparent/api)

### Replicate

- **Route and sign-in:** Replicate provides an official hosted MCP at https://mcp.replicate.com/sse and the official local package replicate-mcp. The hosted route authorizes with a Replicate API token; the local server uses a token in its process environment.
- **Models and cost:** The catalog includes official and community models, including FLUX, GPT Image, Ideogram, and Recraft. Prices depend on the model and may be per output image or by compute time. Current examples include FLUX Schnell at about $0.003 per image, FLUX Dev at about $0.025, and GPT Image 1.5 at about $0.013 low, $0.05 medium, or $0.136 high.
- **References, editing, and alpha:** Model-dependent. GPT Image 1.5 accepts input images and a transparent-background option; other models vary. Replicate also hosts image-background removal models, such as Bria at about $0.018 per image.
- **Limits:** The model’s schema sets image size, reference count, and output count. Replicate’s client can upload local input files up to 100 MB, but an individual model may have a lower limit.

Sources: [official MCP guide](https://replicate.com/docs/reference/mcp) · [official pricing](https://replicate.com/pricing) · [GPT Image 1.5 model page](https://replicate.com/openai/gpt-image-1.5) · [input files](https://replicate.com/docs/topics/predictions/input-files) · [Bria background remover](https://replicate.com/bria/remove-background)

### Black Forest Labs FLUX

- **Route and sign-in:** BFL’s official hosted MCP is https://mcp.bfl.ai; users sign in with BFL OAuth and choose the billing organization. The current MCP documentation lists FLUX.2 models and FLUX 3 video. It does not list the newer FLUX 3 Image model. Direct API calls use a BFL API key.
- **Models and cost:** The official API includes FLUX.2 Pro, Max, Flex, Klein, and FLUX 3 Image. FLUX 3 Image is billed by output tier, from about $0.041 for 768-square to $0.607 at the 4K tier. FLUX.2 pricing depends on model and megapixels.
- **References, editing, and alpha:** FLUX.2 supports editing and multiple references. FLUX 3 Image accepts up to ten references and supports targeted edits. The checked BFL docs do not document native transparent output; use a remover and verify alpha.
- **Limits:** FLUX.2 output is capped at 4 megapixels. FLUX 3 Image offers output tiers up to about 16 megapixels; its API accepts references up to 16 megapixels each. **Setup route:** uses FLUX.2 Pro, sends one reference image, and enforces the 4-megapixel limit.

Sources: [official FLUX MCP](https://github.com/black-forest-labs/flux-mcp) · [FLUX 3 Image](https://bfl.ai/models/flux-3-image) · [BFL pricing](https://bfl.ai/pricing) · [FLUX.2 API guide](https://docs.bfl.ai/api-reference/models/generate-or-edit-an-image-with-flux2-%5Bflex%5D-recommended-for-editing)

### Stability AI

- **Route and sign-in:** Use Stability’s official REST API with a Stability API key. No first-party image-generation MCP was found. A community server exists, but its maintenance and API coverage vary; the app should prefer a reviewed adapter to the current v2beta API.
- **Models and cost:** Current API choices include Stable Image Core, Ultra, and Stable Diffusion 3.5 variants. Listed prices are credit-based at $0.01 per credit: about $0.03 for Core, $0.08 for Ultra, and $0.065 for SD 3.5 Large. The remover costs about $0.05.
- **References, editing, and alpha:** The vendor API also offers Stable Diffusion 3.5 and other edit routes. Image-to-image, inpainting, outpainting, structure, sketch, and style guidance depend on the endpoint. Generation does not document a native alpha setting; Remove Background returns a transparent image. **Setup route:** supports Stable Image Core and Ultra, sends one reference image on supported edits, and includes background removal. Other Stability models remain available through their own clients.
- **Limits:** Core and Ultra use a fixed set of aspect ratios with outputs around one megapixel. Request and edit limits vary by endpoint. Some input image operations cap images at four megapixels; the API reference also documents a 10 MiB request-body error threshold.

Sources: [Stability image API](https://platform.stability.ai/docs/getting-started/stable-image) · [pricing](https://platform.stability.ai/pricing) · [API reference](https://platform.stability.ai/docs/api-reference) · [community MCP candidate](https://github.com/alesurli/mcp-stability-ai)

### Ideogram

- **Route and sign-in:** Ideogram offers an official hosted MCP at https://mcp.ideogram.ai/mcp, authenticated with Ideogram account OAuth. It uses subscription credits. The REST API is a separate API-key and usage-billing route.
- **Models and cost:** Current models include Ideogram 4.5 and 4.0, plus faster or earlier model routes. Standard 4.5 generation costs about $0.03–$0.10 per image by quality. The model is especially useful for text in images and precise edits.
- **References, editing, and alpha:** Supports edits and reference images. Ideogram 4.5 editing accepts up to four references. Ideogram 4.0 has a transparent-background endpoint that returns a real PNG with transparency. **Setup route:** sends one reference image per edit and uses the transparent generation endpoint.
- **Limits:** Standard generation supports 1K and 2K; the dedicated transparent endpoint has resolution tiers through 8K. Transparent API prices range from about $0.03 to $0.42 by quality and size. API image URLs expire, so download the output.

Sources: [official MCP](https://ideogram.ai/features/mcp/) · [API overview](https://developer.ideogram.ai/ideogram-api/api-overview) · [transparent endpoint](https://developer.ideogram.ai/v1/api-reference/generate-images/generate-transparent-v4) · [API pricing](https://ideogram.ai/pricing?pricing_tab=api)

### Recraft

- **Route and sign-in:** Recraft offers an official hosted MCP at https://mcp.recraft.ai/mcp. It uses OAuth and Recraft subscription credits. Its REST API uses an API key and separately purchased API units.
- **Models and cost:** Current raster and vector families include Recraft V4 and V4.1. API prices include about $0.035 for a standard V4.1 raster image, $0.08 for V4.1 vector, and higher prices for Pro. Editing and background removal have separate charges.
- **References, editing, and alpha:** The MCP supports raster and vector generation, image-to-image, inpainting, background operations, vectorization, and upscaling. Style references support up to ten images, up to 20 MB each, and up to 64 MB total. No native transparent-generation setting was documented; the server’s background-removal tool is the supported cutout route.
- **Limits:** The API accepts one to six outputs per request. V4 standard output is about 1K and V4 Pro about 2K; exact supported sizes depend on model. Background removal is about $0.01 per image.

Sources: [MCP setup](https://www.recraft.ai/docs/mcp-reference/getting-started) · [MCP tools](https://www.recraft.ai/docs/mcp-reference/tools) · [API limits](https://www.recraft.ai/docs/api-reference/endpoints) · [API pricing](https://www.recraft.ai/pricing?tab=api)

### Leonardo.Ai

- **Route and sign-in:** Leonardo documents an official MCP at https://mcp.leonardo.ai/v1/mcp. The connector uses a Leonardo API key. API access is pay-as-you-go and separate from the consumer web subscription.
- **Models and cost:** The MCP documentation lists Lucid Origin, Lucid Realism, and Ideogram 3.0. The broader API offers more models, including FLUX and Phoenix. API cost depends on model and settings; the response includes the cost charged, and the Leonardo API calculator estimates it before a call.
- **References, editing, and alpha:** The API supports image guidance, edits, style, content, and character controls; compatible models can generate a transparent foreground. **Setup route:** currently generates with Lucid Origin and does not expose reference edits or transparent output. Use Leonardo’s connector directly for the other API features.
- **Limits:** The API’s common width and height range is 512–1,536 pixels per side, in multiples of 8; some operations can upscale beyond the input dimensions. Reference limits vary by model and guidance type.

Sources: [official MCP setup](https://docs.leonardo.ai/docs/connect-to-leonardoai-mcp) · [API and pricing overview](https://www.leonardo.ai/api) · [transparency](https://docs.leonardo.ai/me/docs/generate-images-using-transparency) · [image guidance](https://docs.leonardo.ai/docs/generate-images-using-image-to-image-guidance) · [API parameter reference](https://docs.leonardo.ai/v1.0/docs/commonly-used-api-values)

### Adobe Firefly

- **Route and sign-in:** Firefly Services has an official API. It uses a Client ID and Client Secret to get an Adobe IMS access token; calls include both the API key and bearer token. Adobe’s Run-Workflow MCP is a hosted, enterprise workflow connector at https://run-workflow.adobe.io/mcp and requires an IMS token plus service API key. It can generate or modify image content through configured workflows; it is not a general MCP for every individual image API operation.
- **Models and cost:** Firefly Image Model 5 is the newest image API model documented here and returns native 4-megapixel images. Adobe does not publish a simple per-image Firefly Services API price on the checked developer pages. Ask the Adobe organization admin for the contract and usage rate. Creative Cloud generative credits and API billing are separate.
- **References, editing, and alpha:** Generate API supports style and structure reference images; Image5 uses reference images for image-to-image instruction edits. Fill, expand, object composite, and background-removal workflows are available. The generation guide does not document a native alpha flag. **Setup route:** uses the official Run-Workflow MCP. Its workflow tools vary by the organization’s configuration; ask it to list its available tools first. The packaged route does not add a separate background-removal tool, so use another selected remover and verify alpha.
- **Limits:** Image5 supports native 4 MP generation. Individual APIs have separate upload, reference, and response constraints; some composite operations cap input files at 10 MB. The API is asynchronous and returns temporary result URLs.

Sources: [Firefly Services overview](https://developer.adobe.com/firefly-services/docs/firefly-api/) · [API quickstart and authentication](https://developer.adobe.com/firefly-services/docs/firefly-api/guides/) · [Image5 generation and editing](https://developer.adobe.com/firefly-services/docs/firefly-api/guides/how-tos/cm-generate-image/feature-guide) · [Run-Workflow MCP overview](https://helpx.adobe.com/firefly/web/work-with-enterprise-features/creative-production/run-workflow-mcp-overview.html) · [MCP setup](https://helpx.adobe.com/firefly/web/work-with-enterprise-features/creative-production/install-run-workflow-mcp.html)

### xAI Grok Imagine

- **Route and sign-in:** Use the official xAI API with an xAI API key. No official image-generation MCP was found. The community [grok-mcp](https://github.com/libraz/grok-mcp) is one available connector; the setup app uses its own API adapter.
- **Models and cost:** Current Imagine image generation and editing use Grok Imagine Image 2.0. The model page lists about $0.04 per output image. Earlier image-model pricing may differ; use the selected model’s live page.
- **References, editing, and alpha:** Image editing accepts up to five reference images. No native transparent-background option was documented; use a separate remover.
- **Limits:** Image models support 1K and 2K resolutions. The API’s Imagine overview describes up to ten image outputs per generation request; the app should still call once per asset.

Sources: [Imagine API overview](https://docs.x.ai/developers/model-capabilities/imagine) · [image model and pricing](https://docs.x.ai/developers/models/grok-imagine-image) · [image-generation tool](https://docs.x.ai/developers/tools/image-generation) · [community Grok MCP](https://github.com/libraz/grok-mcp)

### Together AI

- **Route and sign-in:** Together offers an image REST API and official Python and JavaScript SDKs. Use a Together API key. No maintained, provider-specific image MCP was found; the setup app uses the official Images API through its adapter.
- **Models and cost:** The catalog includes FLUX.1, FLUX.2 Pro, Flex, and other hosted image models. Rates vary by model; the listed FLUX.2 Pro route is about $0.03 per image. Some endpoints, including FLUX Schnell, may have limited free access.
- **References, editing, and alpha:** FLUX.2 Pro supports up to eight references and 4 MP output; Flex supports up to ten references. Other models have different inputs. Native alpha is not a general API feature; confirm the selected endpoint schema or use a remover. **Setup route:** uses the text-to-image endpoint and does not upload project references to a public URL.
- **Limits:** Size and reference limits are model-specific. FLUX.2 supports up to 4 MP. One API key can access models with different prices, inputs, and terms.

Sources: [FLUX.2 Pro model page](https://www.together.ai/models/flux-2-pro) · [FLUX.2 Flex model page](https://www.together.ai/models/flux-2-flex) · [official Together client](https://github.com/togethercomputer/together-python)

### OpenRouter

- **Route and sign-in:** OpenRouter has an official hosted MCP at https://mcp.openrouter.ai/mcp, which uses browser authorization, and a separate Images API that uses an API key. Its Chat Completions and Responses image-generation tool is a third route, not an MCP server. The MCP authorization expires after seven days and starts with a $10 spending cap. The setup app uses the Images API route so it can pass project references without publishing them.
- **Models and cost:** The image catalog includes current models such as Nano Banana 2, GPT Image 2.5, and Seedream. Billing follows the chosen provider/model and may be per image, megapixel, or tokens.
- **References, editing, and alpha:** The Images API accepts input references when the selected model supports them. The server tool exposes parameters for transparency and output format, passed to the underlying model; support remains model-dependent. **Setup route:** uses GPT Image 2.5 Sunburst, with reference edits and transparent PNG requests. The saved image is checked for actual transparent pixels.
- **Limits:** Image model and endpoint records list supported aspect ratios, references, parameters, and price. The Setup route offers the selected GPT Image model’s listed ratios; the model chooses pixel dimensions. Check the live endpoint record rather than assuming one OpenRouter-wide size limit.

Sources: [official hosted MCP guide](https://openrouter.ai/docs/guides/overview/mcp-server) · [image API tutorial](https://openrouter.ai/blog/tutorials/image-generation/) · [live image-model list](https://openrouter.ai/docs/api/api-reference/images/list-image-models) · [per-model endpoint pricing and parameters](https://openrouter.ai/docs/api/api-reference/images/list-image-model-endpoints) · [image-generation server tool](https://openrouter.ai/docs/guides/features/server-tools/image-generation)

### Google Vertex AI Imagen

- **Route and sign-in:** Use Vertex AI with Google Cloud credentials and a Google Cloud project. The setup route reads a service-account credential saved in the operating-system credential store. No image-generation MCP was found; the app-managed adapter calls the official API.
- **Models and cost:** Imagen 4 Fast, Standard, and Ultra are billed per image. Current list prices are about $0.02, $0.04, and $0.06 per image, respectively.
- **References, editing, and alpha:** Imagen 4 is text-to-image. Use Gemini image models for conversational edits and references. No native transparent output is documented.
- **Limits:** The app adapter uses the model’s default image size. Check the selected Imagen endpoint for its current output dimensions and regional availability.

Sources: [Imagen 4 model card](https://cloud.google.com/vertex-ai/generative-ai/docs/models/imagen/4-0-generate-001) · [Vertex AI image pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing)

### Microsoft Foundry MAI Image

- **Route and sign-in:** Use the Microsoft Foundry API with Entra sign-in or an API key. The setup app currently uses an API key in the operating-system credential store and needs the resource endpoint and deployed model name. No official image-generation MCP was found.
- **Models and cost:** MAI-Image-2.6 and MAI-Image-2.6-Flash are in public preview. Billing depends on the deployment and changes as the service moves out of preview.
- **References, editing, and alpha:** The service supports text-to-image and edits with up to five references. Native alpha is not documented. The setup route supports one source image per edit.
- **Limits:** The documented 2.6 preview output limit is about 2.36 megapixels. The setup adapter caps requests to that area.

Sources: [Microsoft Foundry MAI image guide](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-mai-image) · [Microsoft Foundry pricing](https://azure.microsoft.com/en-us/pricing/details/ai-foundry/)

### Amazon Bedrock Stability image services

- **Route and sign-in:** Amazon Bedrock hosts Stability image models and image-edit services. The setup adapter signs requests with AWS credentials saved in the operating-system credential store and a selected AWS region. AWS publishes a maintained [Bedrock image MCP server](https://github.com/awslabs/bedrock-image-mcp-server); the setup app uses its own adapter for the image calls and exposes background removal as a tool.
- **Models and cost:** Current routes include Stable Image Core, Stable Image Ultra, Stable Diffusion 3.5 Large, and paid edit services. AWS charges by model and image operation; prices vary by region. Do not use Titan Image Generator or Nova Canvas, which have passed their end-of-life dates.
- **References, editing, and alpha:** The vendor service includes Stable Diffusion 3.5 image edits as well as Stable Image Ultra edits. The current Setup adapter supports one reference with Ultra; Core is text-to-image only. Generation does not offer native alpha; the separate Stable Image Remove Background model returns a cutout. The adapter checks the saved PNG for actual transparent pixels. SD 3.5 remains available through a client that supports its model-specific request format.
- **Limits:** Core and Ultra accept 640–1,536 pixel dimensions and supported aspect ratios; Stable Diffusion 3.5 Large outputs about 1 megapixel. The setup route uses the model’s default size and limits the background-removal input to the provider’s published pixel and shape bounds.

Sources: [AWS Stability image services](https://docs.aws.amazon.com/bedrock/latest/userguide/stable-image-services.html) · [Stable Image Ultra request and response](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-diffusion-stable-ultra-text-image-request-response.html) · [Stable Diffusion 3.5 request and response](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-diffusion-3-5-large.html) · [Bedrock image pricing](https://aws.amazon.com/bedrock/pricing/) · [Nova Canvas lifecycle](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-canvas.html)

### Hugging Face Inference Providers

- **Route and sign-in:** Use a Hugging Face token saved in the operating-system credential store. The service routes requests to a changing set of model providers. No dedicated official image-generation MCP was found; the setup app uses its own API adapter.
- **Models and cost:** The catalog includes open image models served by partner providers. Billing is pay-as-you-go; the rate depends on the model and selected provider.
- **References, editing, and alpha:** Each model has its own input and output schema. The setup route currently exposes text-to-image only; use a provider-specific edit route or another selected provider for references and background removal.
- **Limits:** Image size, file inputs, and output format depend on the chosen model. The route’s size field is model-defined, so check the live model page before using it.

Sources: [Inference Providers overview](https://huggingface.co/docs/inference-providers/index) · [pricing and billing](https://huggingface.co/docs/inference-providers/pricing)

## Local image servers

### ComfyUI

- **Route and sign-in:** ComfyUI runs on the user’s machine. The Comfy Organization publishes an open-source local MCP server in [Comfy-Org/comfy-mcp](https://github.com/Comfy-Org/comfy-mcp). It can connect an agent to local ComfyUI; Comfy Cloud is a separate paid remote route.
- **Cost and models:** Local generation has no per-image service charge; the user supplies compatible hardware and model files. Model license terms vary. A Cloud route uses its own plan or credits.
- **References, editing, and alpha:** ComfyUI workflows can use image references, inpainting, control nodes, and transparent output where the installed model and graph support them. The app should use the user’s workflow schema and check the actual image pixels.
- **Limits:** Model, graph, custom-node, and hardware limits apply. There is no single ComfyUI resolution or reference count.
- **HOI4 portrait workflow:** The user’s [ComfyUI HOI4 Portraits package](https://github.com/klimPaskov/comfyui-hoi4-portraits) is a specialized source and processing workflow for HOI4 portraits. Its published contract does not authorize text-to-image generation for fictional portraits; keep its portrait rules distinct from general art generation.

Sources: [Comfy-Org local and Cloud MCP](https://github.com/Comfy-Org/comfy-mcp) · [HOI4 portrait workflows](https://github.com/klimPaskov/comfyui-hoi4-portraits)

### Automatic1111 and Forge

- **Route and sign-in:** These are local Stable Diffusion web servers. They do not provide a first-party MCP server. A1111 exposes a local HTTP API when launched with its API option; Forge has compatible local API routes. The app can use a reviewed local adapter, bound to loopback.
- **Cost and models:** No service image fee. Costs are local hardware and storage; users download their own checkpoints, LoRAs, and extensions and must follow each model’s license.
- **References, editing, and alpha:** txt2img, img2img, inpainting, masks, and extensions are available through model and extension settings. Transparency depends on the model, extension, and saving workflow.
- **Limits:** VRAM, model architecture, and enabled extensions determine resolution and input limits. Read the running server’s API schema instead of hardcoding one maximum.

Sources: [A1111 API guide](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API) · [Forge API documentation](https://stablediffusionwebuiforge.com/api/) · [Forge source](https://github.com/lllyasviel/stable-diffusion-webui-forge)

## Manual route and unsupported automation

### None — I will make the art myself

No provider, login, key, server, or model cost. The user supplies their own raster or vector artwork. The asset workflow still validates file format, dimensions, and alpha when those properties matter.

### Midjourney — manual use only

Do not register an MCP or automate Midjourney through Discord or the website. Midjourney says it has no public API planned, and its Terms prohibit automated tools from accessing, interacting with, or generating assets through the service. A user can generate manually in Midjourney and then add the downloaded files to the project.

Sources: [Midjourney FAQ](https://github.com/midjourney/docs/blob/main/data/faq.txt) · [Terms of Service](https://docs.midjourney.com/docs/terms-of-service)

## Not a current choice: Amazon Nova Canvas

Amazon Nova Canvas is a serious image model with text-to-image, image editing, references, and a transparent background-removal task. AWS documentation marks its model lifecycle as **Legacy** with an EOL date of 2026-09-30, before this document’s checked date. Do not offer it as a current provider unless AWS publishes a supported replacement.

Sources: [Nova Canvas model card and lifecycle](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-canvas.html) · [image capabilities and output limits](https://docs.aws.amazon.com/nova/latest/userguide/image-generation.html) · [AWS Labs MCP migration note](https://github.com/awslabs/mcp/blob/main/docs/migration-nova-canvas.md)

## Shared rules for generated HOI4 assets

- Ask for and save one finished asset per image call, even when a service supports batches.
- Pass each reference image by a numbered role, such as “Image 1 is the character reference; Image 2 is the style reference.” Follow the chosen model’s input format and limits.
- Request a transparent background only when the selected route supports it. Save PNG or WebP as required by that provider.
- A prompt that says “transparent” or a checkerboard-looking image is not proof of transparency. Inspect the saved file’s alpha channel. If it is opaque or the model does not support alpha, use the selected provider’s background-removal tool or a local matte, then inspect alpha again.
- Keep an exact model/endpoint identifier with cost and limit notes in the app’s provider table. Refresh those notes when updating a pinned MCP or API adapter.

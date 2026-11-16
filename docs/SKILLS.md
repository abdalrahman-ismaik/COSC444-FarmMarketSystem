# Skills and source provenance

## Project-local skills

The approved repository pass copies two reusable skills from KU Planner's Windows bootstrap distribution. It does not run the bootstrap installer or transfer that project's app instructions, credentials, global settings, dependencies, or Liquid Glass theme.

| Skill | Local entry point | Original local source | Use |
|---|---|---|---|
| Impeccable | [SKILL.md](../.agents/skills/impeccable/SKILL.md) | `C:/Users/4bais/kuplannar/opencode-student-bootstrap/Windows/skills/impeccable/` | Desktop theme documentation and future interface work; preserve Tkinter context |
| Ponytail | [SKILL.md](../.agents/skills/ponytail/SKILL.md) | `C:/Users/4bais/kuplannar/opencode-student-bootstrap/Windows/skills/ponytail/` | Keep implementation and repository structure simple; do not remove rubric requirements |

Directories are copied with their supporting references/scripts/agent instructions, not just the entry Markdown. The source distribution and copied files are hash-checked in this pass. No provider credentials or paid generation jobs are needed for the documentation. Skills are project-local and available for discovery in subsequent turns; global skills are not overwritten.

The installed PDF skill at `C:/Users/4bais/.codex/skills/pdf/SKILL.md` was used to guide source-document review. It is already available in the environment and was not copied from KU Planner. No video, hosting, image-generation, or presentation-production workflow is needed to organize this repository.

Skill instructions remain subordinate to user scope, environment rules, and actual project requirements. Automated design checks intended for CSS/web projects do not establish Tkinter accessibility or visual correctness.

## Course and application materials

| Material | Preserved location | Interpretation |
|---|---|---|
| Four-page proposal | [Original PDF](sources/Local_Farm_Market_Food_Availability_Project_Proposal.pdf) | Primary project requirements |
| Twelve-slide Lab 6 deck | [Original PPTX](sources/langchain.pptx) | Teaching context for Gemini/MySQL natural-language queries |
| Supplied announcements | [Announcement record](ANNOUNCEMENTS.md) | Later logistics and detailed rubric; external form state unverified |
| Original application package | `archive/original-package/FarmMarketSystem_Team.zip` | Immutable baseline for preservation comparisons |
| Original application README | [Archived README](../archive/original-package/README.md) | Historical instructions; root README is maintained |
| Existing 37-page visual guide | [Visual_Guide.pdf](reference/Visual_Guide.pdf) | Historical screenshots and reported tests; known demo-order issue, stand-in AI disclosure |
| School-database starter | `archive/lab-example/` | Teaching code/schema/data; not the maintained farm app |

## Sample-image attribution

The supplied SQL, README, and visual guide attribute the photographs to **Fruits-360**, under **Creative Commons Attribution-ShareAlike 4.0**. The preserved material does not contain exact upstream download URLs, image identifiers, creator details, or a full attribution/license file. Do not claim those have been verified.

There are twelve product-image BLOBs embedded in SQL and four external JPEGs for upload demonstrations. All image bytes are preserved. Before redistributing the final project, confirm exact dataset version, creator attribution, source image mapping, and applicable license/redistribution requirements; add a verified attribution record. Do not assign a blanket project license to these images or instructor materials. No new license grant for application code has been inferred.

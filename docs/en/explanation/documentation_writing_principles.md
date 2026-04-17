# Documentation Writing Principles

This document explains how documentation in `driving-preference-field` should be written. If `engineering_operating_principles.md` governs how the repo moves without drifting, this document governs how a page should answer the reader’s question clearly enough for both humans and tools to reconstruct the current truth.

The primary rule is simple: documentation exists to answer a question. A page that does not make its question explicit will usually sprawl into mixed roles. Explanation pages should answer why something exists or how to think about it. Reference pages should answer what the contract is. How-to pages should answer how to complete a task. Status pages should answer where the project currently stands. Reading and internal pages should stay clearly non-canonical.

One paragraph should answer one question. When several claims are packed into one block, both readability and future maintenance degrade. Shorter paragraphs, direct topic sentences, and deliberate sectioning matter more here than decorative formatting.

The reader should be able to locate the main point early. The first paragraph should normally state what the page is for, why it matters, and what it will or will not cover. If those points are only discoverable after several sections, the page is too hard to enter.

Task-first pages and reference-first pages should not be mixed. A guide that turns into a catalog is harder to use, and a reference page that turns into a long essay is harder to search. When a page begins to serve two roles, split the roles rather than stretching the page further.

The same concept may appear in more than one document, but the density should match the page role. Repetition is acceptable when it helps a newcomer enter the topic or helps a reference page stand on its own. Contradiction is not acceptable.

When a proposed doc change affects repo-wide terminology, operating workflow, AI guidance, or other user-facing semantics, it should be reviewed before it is applied. That review should check terminology consistency, evidence and rationale, factual accuracy, clarity, and whether the new wording overlaps with or contradicts existing pages.

Documentation here also has to support AI reconstruction, not only human reading. That means concepts, contracts, and current implementation notes should be explicit enough to survive partial context. AI-friendly writing is not a separate style. It is the same discipline that makes documents easier for humans to scan: direct statements, controlled scope, stable terminology, and minimal hidden assumptions.

When a page needs external writing guidance, the references in `docs/en/reading/references/documentation_style_references.md` and its Korean counterpart are the place to check. Those references are supporting material. This document is the repo’s working writing rule.

These writing principles are defaults, not permanent law. If a clearer structure or a better wording appears, the document can change too. The important thing is to update the wording explicitly and keep overlap or contradiction under control.

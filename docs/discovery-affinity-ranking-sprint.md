# Discovery affinity ranking sprint

## Goal

Improve personalized homepage recommendations using only first-party activity already stored by VideoShare, without external recommendation services or weakening visibility rules.

## Delivered

- Category affinity now scales with how often a viewer has watched that category recently.
- Watched-channel affinity can produce recommendations even when a candidate has no tag/category metadata.
- Tag and hashtag overlap receive explicit ranking weight.
- Existing likes, views, recency, and primary-key ordering remain deterministic tie-breakers.
- Watched videos remain excluded from recommendations.
- Candidate selection continues to start from `Video.objects.visible_to(user)`.
- Regression coverage verifies stronger repeated-interest ranking and channel affinity.

## Ranking model

The personalized recommendation score is intentionally simple and explainable:

- category affinity: watched count × 3
- channel affinity: watched count × 2
- matching tag: +2 each
- matching hashtag: +2 each

After affinity score, candidates are ordered by likes, views, publication date, and stable primary-key order.

## Acceptance criteria

- No recommendation may bypass centralized visibility rules.
- Another user's history must not affect the current viewer.
- Watched items remain excluded.
- Repeated interests rank above weaker one-off interests.
- Recommendations stay bounded by the discovery section limit.

# Editorial visual refresh

Creative Studio direction: a restrained editorial video library, preserving the existing coral/violet mark and white-label copy. Existing Django templates and Bootstrap are retained; HeroUI, AlignUI and Ant Design would require an unnecessary React migration, while daisyUI would add a Tailwind build path. No new assets, fonts, runtime or paid service.

Changes: compact media-focused hero with real browse/category actions, consistent card surfaces, stronger section rhythm, scrollable navigation on mobile, explicit keyboard focus, reduced-motion safeguards, responsive text wrapping and full-width empty states. Existing system font stack and favicon retained. No authorization or playback changes.

Verification: Django structural and contrast regression checks plus discovery action tests in CI. Manual browser checks at 390, 768, 1024 and 1440 pixels, keyboard navigation, mobile scrolling, and Docker smoke testing remain required before claiming visual verification.

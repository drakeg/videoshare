# Customer branding assets

Optional deployment settings allow each independent VideoShare installation to use its own logo and favicon without template changes.

1. Place customer-owned PNG, WebP, JPEG or ICO images under `video/static/branding/` in the deployment checkout. Use a square image for the header logo; PNG or ICO is recommended for the favicon.
2. Set `DJANGO_SITE_LOGO=branding/customer/logo.png` and `DJANGO_SITE_FAVICON=branding/customer/icon.ico` in the deployment environment. Paths are relative to static storage, not filesystem paths or URLs.
3. Ensure the files are included when building the image and running collectstatic; restart the service. For the local Compose bind mount, restart the web service to collect static files.
4. Verify the homepage and private sign-in screen at mobile and desktop widths. Empty or invalid settings retain the original mark or favicon. A valid path to a missing file must be corrected by the operator; file existence is not checked on every request.

Remote URLs, traversal paths, and SVG uploads are intentionally unsupported. The assets are public static files, even for private portals: never place confidential content there. No database migrations or new dependencies are required.

CI covers rendering and path rejection; manual browser and Docker checks remain required.

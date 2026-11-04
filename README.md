# Mazo Moon website

The Mazo Moon brand site: journals, colouring books and stationery, sold through Amazon.

- `index.html` holds the whole site (pages switch with `#home`, `#journals`, `#shop`, `#reading`, `#little-things`, `#our-story`).
- `img/` holds photos, book covers, inside pages and sticker cut-outs (`img/cut/`).
- Products and books are listed near the top of the script in `index.html` (`products`, `books`, `little`). Change a price, name or ASIN there.
- Contact and newsletter forms post to FormSubmit (formsubmit.co), which emails each entry to hello@mazomoon.com. The very first submission triggers a one-off activation email that must be confirmed.

Hosted on GitHub Pages at mazomoon.com (see `CNAME`): every push to `main` publishes automatically.
- `links/index.html` is the link-in-bio page for social profiles (mazomoon.com/links). Edit the `links` array in its script to change the buttons.

Deploys: GitHub Pages rebuilds automatically on every push to main. If a deploy stalls, push again.

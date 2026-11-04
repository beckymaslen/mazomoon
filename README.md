# Mazo Moon website

The Mazo Moon brand site: journals, colouring books and stationery, sold through Amazon.

- `index.html` holds the whole site (pages switch with `#home`, `#journals`, `#shop`, `#reading`, `#little-things`, `#our-story`).
- `img/` holds photos, book covers, inside pages and sticker cut-outs (`img/cut/`).
- Products and books are listed near the top of the script in `index.html` (`products`, `books`, `little`). Change a price, name or ASIN there.
- Contact and newsletter forms post to FormSubmit (formsubmit.co), which emails each entry to hello@mazomoon.com. The very first submission triggers a one-off activation email that must be confirmed.

Hosted on GitHub Pages at mazomoon.com (see `CNAME`): every push to `main` publishes automatically.
- `links/index.html` is the link-in-bio page for social profiles (mazomoon.com/links). Edit the `links` array in its script to change the buttons.

Deploys: GitHub Pages rebuilds automatically on every push to main. If a deploy stalls, push again.

## Section pages
Each section has its own address (/shop/, /journals/, /reading/, /little-things/, /our-story/) with its own title and sharing details. These are copies of index.html, so after any change to index.html run:

    python3 tools/build_pages.py

Privacy, Cookies and Terms live in tools/legal.py. Edit the text there, then run `python3 tools/legal.py`.

## Book reviews (blog)
Reviews are written in Pages CMS: go to https://app.pagescms.org, sign in with GitHub and open the mazomoon repo, then "Book reviews". Each review is a file in `content/reviews/`. Turn on "Publish on the website" and save; GitHub then rebuilds the site (`.github/workflows/pages.yml`) and the review appears at /reading/<title>/ and on the Reading Corner, linked from its book. Drafts stay off the site. The book dropdown in `.pages.yml` is refreshed from the shelf by `tools/build_pages.py`. Photos go in `img/reviews/`.

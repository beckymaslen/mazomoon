# Mazo Moon website

The Mazo Moon brand site: journals, colouring books and stationery, sold through Amazon.

- **Home page (`/`) is the interactive desk.** Its markup and styles are in `src/desk-body.html`; its words, products, prices and links are in `desk/content.js`; its code is `desk/app.js`; its pictures are in `desk/img/`. `index.html` and `desk/reviews.js` are built from these, so don't edit them by hand.
- **Section pages** (/shop/, /journals/, /reading/, /little-things/, /our-story/) come from `src/site.html` (pages switch with `#journals`, `#shop` ...). Products and books for them are near the top of its script (`products`, `books`, `little`).
- `img/` holds photos, book covers, inside pages and sticker cut-outs (`img/cut/`) for the section pages.
- The monthly letter signs people up in Mailchimp (list "Mazo Moon"). Contact forms post to FormSubmit (formsubmit.co), which emails each entry to hello@mazomoon.com.
- `consent.js` is on every page: the cookie banner, Google Analytics (only after Accept), the `amazon_click` and `sign_up` events, and the Amazon Attribution tags. To report an advert on its own, add its utm_campaign name and Attribution tag to `CAMPAIGN_TAGS` there.

Hosted on GitHub Pages at mazomoon.com (see `CNAME`): every push to `main` publishes automatically.
- `links/index.html` is the link-in-bio page for social profiles (mazomoon.com/links). Edit the `links` array in its script to change the buttons.

Deploys: GitHub Pages rebuilds automatically on every push to main. If a deploy stalls, push again.

## Section pages
Each section has its own address (/shop/, /journals/, /reading/, /little-things/, /our-story/) with its own title and sharing details. These are copies of src/site.html, so after any change to src/site.html, src/desk-body.html or a review, run:

    python3 tools/build_pages.py

Privacy, Cookies and Terms live in tools/legal.py. Edit the text there, then run `python3 tools/legal.py`.

## Book reviews (blog)
Reviews are written in Pages CMS: go to https://app.pagescms.org, sign in with GitHub and open the mazomoon repo, then "Book reviews". Each review is a file in `content/reviews/`. Turn on "Publish on the website" and save; GitHub then rebuilds the site (`.github/workflows/pages.yml`) and the review appears at /reading/<title>/ and on the Reading Corner, linked from its book. Drafts stay off the site. The book dropdown in `.pages.yml` is refreshed from the shelf by `tools/build_pages.py`. Photos go in `img/reviews/`.

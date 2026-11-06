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

## Blog and book reviews
Posts are written in Pages CMS: go to https://app.pagescms.org, sign in with GitHub, open the mazomoon repo, then "Posts and reviews". Each post is a file in `content/reviews/` (the folder name stayed the same so old links keep working). Alongside it the editor has Categories (`content/categories/`), Writers (`content/authors/`), the Product Library (`content/products/`) and Shops and affiliate programmes (`content/partners/`).

- **Post types:** book review, product review, product roundup, blog or lifestyle post, reading guide, list and editorial. Book reviews live at /reading/<address>/, everything else at /blog/<address>/, with the blog home at /blog/ and a page per category at /blog/topics/<category>/.
- **Status:** Draft, Scheduled (goes live by itself at its date and time; the publish workflow checks every hour), Published, or Archived (page kept, hidden from lists and Google).
- **Preview and checklist:** every post gets an unlisted, noindex preview at /preview/<file name>/ with the checklist, Google and sharing previews, a promotion pack (Pinterest, Instagram, newsletter text with tracked links) and a phone view. The "Check this post" button in the editor runs `.github/workflows/post-check.yml` and writes the same checklist to the run summary.
- **Blocking problems** (no writing, no book on a review, a clashing web address, a missing shop, stars on something not used, gifted or paid with no brand named) keep a post off the site until fixed; everything else is a suggestion.
- **Affiliate links:** products and their shop links are entered once in the Product Library. Affiliate links get `rel="sponsored"`, an "Ad" note and the shop's own statement (Amazon's "As an Amazon Associate I earn from qualifying purchases."). Product reviews and roundups with affiliate links, and gifted or paid posts, get an "Ad" label at the top and on their cards. Clicks are sent to Google Analytics as `affiliate_click` (only after cookie consent).
- **Built automatically:** reading time, author, series and series position from the shelf, search title and description, canonical, robots (max-image-preview:large), Open Graph, Review/BlogPosting/Product and breadcrumb JSON-LD, sitemap with images, the RSS feed at /reading/feed.xml, posts.json, related posts and books, series navigation, a 1200 x 630 sharing image cut from the featured photo, and redirects from old addresses.

All of this is in `tools/blog.py`; `python3 tools/blog.py --check` prints the checklist locally. The book dropdown in `.pages.yml` is refreshed from the shelf on every build. Photos go in `img/reviews/`.

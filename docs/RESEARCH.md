# Research notes (2026-11-26)

## Threads API

- Official, free. Publishing is two calls: `POST /{user-id}/threads` (container) then `POST /{user-id}/threads_publish`. A reply is the same with `reply_to_id`.
- Limits per profile per rolling 24 h: 250 posts, 1,000 replies, 100 deletes. Posts are 500 characters.
- Insights: `GET /{media-id}/insights?metric=views,likes,replies,reposts,quotes,shares`.
- Keyword search of public posts needs `threads_keyword_search` approval (App Review); without it only your own posts are searchable. Trends therefore come from Google Trends + news RSS instead.
- Tokens: short-lived (1 h) -> long-lived (60 days) via `th_exchange_token`; refresh with `th_refresh_token` once at least 24 h old.

## This repo's Meta app

- App "Content Engine", app id 4949758248504156, Threads App ID 1219331693984614, unpublished (development mode), no business portfolio.
- Permissions: threads_basic, threads_content_publish, threads_manage_insights, threads_manage_replies, threads_read_replies. Redirect `https://localhost/`.
- Account A @goycoon is a Threads Tester. For account B: App roles -> Add People -> Threads Tester -> accept under Threads Settings -> Account -> Website permissions -> Invites, then `meta auth B`.

## Monetising in Vietnam

- Threads pays no creator money in Vietnam (the bonus programme was invite-only and US-first).
- Realistic income: Shopee / Lazada / TikTok Shop affiliate links in replies (Shopee reportedly wants about 2,000 followers and a 28-day-old account), brand deals once there is a niche audience, sending traffic to your own product or community.
- Selling an account breaks the Instagram/Threads terms.

## Trend sources that work from this machine

Google Trends daily RSS for VN, VnExpress (tin nổi bật, giải trí), Kenh14, Thanh Niên, Tuổi Trẻ, GenK. Reddit RSS is blocked.

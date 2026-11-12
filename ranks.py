"""The AI without BS rank scale, best to worst. One source of truth for build_reviews.py and merge_v2.py.
Each review's rank lives in reviews_src/content/<slug>.json as "verdict_tier" and must be one of TIERS."""
RANKS=[
 ("Incredible","Best in its class. Worth paying for if you need it."),
 ("Must use","Get it today. It earns its keep from day one."),
 ("Badass","Does one job really well. Point it at that job."),
 ("It's alright","Useful in the right setup. Don't rearrange your life for it."),
 ("Could be left alone","Only if you already live in it. Otherwise, skip."),
 ("You're doing too much","More hype than help. Walk away."),
]
TIERS=[r for r,_ in RANKS]
MEANING=dict(RANKS)
def rank_no(tier): return TIERS.index(tier)+1          # 1 = best
def rank_cls(tier): return f"rank r{rank_no(tier)}"    # CSS class for the badge

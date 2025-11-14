"""
Example CRE deal texts for testing and demos
"""

EXAMPLE_MULTIFAMILY_AUSTIN = """Hey, I just got off the phone with Marcus from JLL. He's got a deal in Austin, Texas
that might be interesting for us. It's a 148-unit multifamily property, Class B plus, built in 2008.
The property is currently 92% occupied and generating about $1.2 million in NOI.

They're asking $18.5 million, which puts it at a 6.5% cap rate. Location is solid - it's in the
Domain area, close to Apple's campus and a bunch of other tech companies. Units are mostly
two-bedroom, two-bath layouts, averaging around 950 square feet.

The seller is a regional operator looking to exit and redeploy capital. Marcus mentioned there's
some deferred maintenance, maybe $400K to $500K to get it to where we'd want it. Rents are
slightly below market - he thinks there's opportunity to push another $75 to $100 per unit.

They're looking for offers by next Friday. Marcus's email is marcus.thompson at jll.com. He said
he can get us the full OM by tomorrow if we're interested. Let me know if you want me to dig deeper."""


EXAMPLE_INDUSTRIAL_PHOENIX = """Following up on our call - the Phoenix industrial deal looks promising. It's a
125,000 SF warehouse facility in the West Valley submarket, built in 2015. Single tenant,
national credit (Amazon), on a 10-year triple-net lease with 5% bumps every 3 years.

Current rent is $8.50/SF, which is slightly below market. NOI is running around $950K annually.
Seller is asking $14.8M - that's a 6.4% cap rate. The property is 100% occupied with 7 years
remaining on the lease.

Location is excellent for last-mile distribution - right off the 10 freeway with easy access to
downtown Phoenix and Scottsdale. The broker, Jennifer Kim from CBRE (jennifer.kim at cbre.com),
says there's significant interest and they're expecting multiple offers.

One thing to note - there's a small amount of deferred capex on the roof, probably $150K-$200K,
but otherwise the building is in great shape. Clear height is 32 feet, plenty of dock doors, and
modern warehouse spec. This one fits our buy-box really well."""


EXAMPLE_OFFICE_MIAMI = """Got a cold call from a broker at Cushman & Wakefield about an office building in
Miami, Florida. It's a 75,000 SF Class A office in Brickell, built in 2019. The asking price is
$32 million.

Current occupancy is only 68%, which is a bit concerning. They're showing an NOI of $1.5M, but
that's pro forma based on stabilized occupancy at 95%. Actual in-place NOI is probably closer to
$1.1M given the vacancy.

At $32M on $1.5M NOI, they're pitching a 4.7% cap rate, but on actual NOI it's more like 3.4%.
That's pretty aggressive for office right now, especially with the vacancies. The broker mentioned
the seller is willing to carry some paper if needed.

The building does have some nice features - floor-to-ceiling glass, high-end finishes, structured
parking. But I'm not sure office in Miami at sub-5% cap makes sense for us right now. Might pass
on this one unless they come down significantly on price."""


EXAMPLE_RETAIL_DALLAS = """Quick summary from today's tour of the Dallas retail center. It's a neighborhood
shopping center in Plano, Texas - about 42,000 square feet anchored by a Kroger grocery store.

The center is 95% occupied. Kroger has 15 years left on their lease with 2% annual increases.
The rest of the inline tenants are a mix of service retail - hair salon, dry cleaner, pizza place,
pet grooming, etc. Pretty stable tenant mix.

Asking price is $8.7 million on an NOI of $615,000, so we're looking at about a 7.1% cap rate.
The location is solid - it's in an affluent residential area with strong demographics. Household
incomes within 3 miles are over $120K.

The broker is Sarah Chen from Newmark (sarah.chen at newmark.com). She mentioned they have another
group looking at it, but we'd be the preferred buyer if we can move quickly. Built in 2005, so
it's in good condition. Parking lot needs restriping and some landscaping updates, but nothing major.

I think this could work for us - the Kroger anchor provides stability and the cap rate is in our
target range. Let me know if you want me to request the full package."""


EXAMPLE_MIXED_USE_DENVER = """Following up on the Denver mixed-use opportunity. This is a really interesting
asset - ground floor retail (8,500 SF) with 24 luxury apartments above. Located in the LoHi
neighborhood, which is one of Denver's hottest submarkets.

Retail is 100% leased to two tenants: a popular local restaurant and a boutique fitness studio.
The apartments are 96% occupied, mostly young professionals. Built in 2017, so it's almost new.

The numbers: Purchase price of $11.2M, combined NOI of $725K from both retail and residential.
That's a 6.5% cap rate. The residential rents are averaging $2,400/month for 1-beds and $3,200
for 2-beds, which is right at market.

Broker is David Martinez from JLL, email is david.martinez at jll.com. He says the seller is a
local developer who's moving on to their next project and is motivated to close quickly.

The only concern is that mixed-use can be harder to manage and finance. But the location is
phenomenal - walkable to everything, great restaurants and bars nearby, mountain views from the
upper units. Could be a solid addition to the portfolio if we're comfortable with the mixed-use
format."""


def get_all_examples():
    """Return a dictionary of all example texts"""
    return {
        "Austin Multifamily (148 units, 6.5% cap)": EXAMPLE_MULTIFAMILY_AUSTIN,
        "Phoenix Industrial (125k SF, Amazon tenant, 6.4% cap)": EXAMPLE_INDUSTRIAL_PHOENIX,
        "Miami Office (75k SF, HIGH vacancy, 3.4% cap)": EXAMPLE_OFFICE_MIAMI,
        "Dallas Retail (Kroger-anchored, 7.1% cap)": EXAMPLE_RETAIL_DALLAS,
        "Denver Mixed-Use (Retail + 24 units, 6.5% cap)": EXAMPLE_MIXED_USE_DENVER,
    }

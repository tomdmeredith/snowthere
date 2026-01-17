-- Resort Content - Written in "Instagram Mom" Voice
-- Run after seed.sql to populate content

DO $$
DECLARE
    park_city_id UUID;
    st_anton_id UUID;
    zermatt_id UUID;
BEGIN
    SELECT id INTO park_city_id FROM resorts WHERE slug = 'park-city';
    SELECT id INTO st_anton_id FROM resorts WHERE slug = 'st-anton';
    SELECT id INTO zermatt_id FROM resorts WHERE slug = 'zermatt';

    -- ============================================
    -- PARK CITY CONTENT
    -- ============================================
    INSERT INTO resort_content (
        resort_id, quick_take, getting_there, where_to_stay,
        lift_tickets, on_mountain, off_mountain,
        parent_reviews_summary, faqs, seo_meta, content_version
    ) VALUES (
        park_city_id,
        -- quick_take
        '<p>Here''s the thing about Park City - it''s basically the family ski vacation on easy mode. You''ve got 7,300 acres (yes, it''s MASSIVE), an actual town with real restaurants and shops, and it''s only 35 minutes from Salt Lake City airport. No winding mountain roads, no altitude sickness drama.</p>
        <p>The catch? It''s not cheap. Like, at all. But if you''re doing a big US ski trip and want to minimize logistics headaches while maximizing fun, Park City delivers.</p>
        <p><strong>Real talk:</strong> Your 5-year-old will be fine here. Your teenager will actually have fun. And you might even get a date night at one of the incredible restaurants on Main Street.</p>',

        -- getting_there
        '<p><strong>Pro tip:</strong> Fly into Salt Lake City (SLC). It''s one of the easiest ski-to-airport experiences in the US.</p>
        <ul>
        <li><strong>From SLC:</strong> 35-40 minutes via I-80. Uber works fine, or grab a rental car if you want flexibility.</li>
        <li><strong>Shuttle options:</strong> Canyon Transportation and PC Express both run regular shuttles (~$50/person each way).</li>
        <li><strong>Rental car:</strong> Honestly? Nice to have for grocery runs, but not essential if you''re staying in town.</li>
        </ul>
        <p><strong>Warning:</strong> I-80 can close in bad weather. Check UDOT before heading up.</p>',

        -- where_to_stay
        '<p>You''ve got two vibes here: historic Main Street or ski-in/ski-out at the base.</p>
        <h3>For Families on a Budget</h3>
        <p><strong>The Chateaux at Silver Lake</strong> - Condos with kitchens (hello, savings on breakfast). Not the fanciest, but clean and well-located.</p>
        <h3>The Sweet Spot</h3>
        <p><strong>Hyatt Centric Park City</strong> - Right on Main Street, pool for the kids, walkable to everything. Our top pick for families who want convenience.</p>
        <h3>If You''re Treating Yourself</h3>
        <p><strong>Montage Deer Valley</strong> - Technically Deer Valley, but wow. Kids club, slope-side, s''mores by the fire pit. Worth it for a special trip.</p>
        <p><strong>Real talk:</strong> Airbnb can work well here for larger groups. Look for condos near the town lift.</p>',

        -- lift_tickets
        '<p>Let''s be real - Park City isn''t cheap. But here''s how to make it hurt less:</p>
        <h3>Daily Rates (Window Price)</h3>
        <ul>
        <li>Adult: $239/day (yes, really)</li>
        <li>Child (5-12): $149/day</li>
        <li>Under 5: FREE</li>
        </ul>
        <h3>The Smart Play: Epic Pass</h3>
        <p>If you ski more than 3-4 days a year, the Epic Pass is a no-brainer. Park City has unlimited access, and you get days at Vail, Whistler, and European resorts too.</p>
        <ul>
        <li><strong>Epic Pass:</strong> ~$979/adult (unlimited days)</li>
        <li><strong>Epic Day Pass:</strong> Starting around $67/day if you buy early for specific dates</li>
        </ul>
        <p><strong>Pro tip:</strong> Buy your Epic Pass in spring for the best price. They increase prices throughout summer.</p>',

        -- on_mountain
        '<p>Park City + Canyons combined is HUGE. Like, "you could ski here a week and not repeat a run" huge.</p>
        <h3>For Beginners</h3>
        <p>Head to <strong>First Time</strong> area near the base. Magic carpet, gentle terrain, and ski school pick-up right there. The <strong>Three Kings</strong> area is perfect for kids graduating from bunny slopes.</p>
        <h3>For Intermediate Kids</h3>
        <p><strong>King Con Ridge</strong> has great blues that feel adventurous without being scary. <strong>Jupiter Peak</strong> for your confident 10-year-old who wants to feel like a big kid.</p>
        <h3>Ski School</h3>
        <p>Book in advance! Seriously, during holidays it sells out. They have programs starting at age 3.</p>
        <ul>
        <li><strong>Little Adventures (3-4):</strong> Half-day intro, super gentle</li>
        <li><strong>Mountain Explorers (5-6):</strong> Full day, lunch included</li>
        <li><strong>Mountain Riders (7-14):</strong> They''ll actually improve here</li>
        </ul>
        <p><strong>Lunch spot:</strong> Meet at Mid-Mountain Lodge. The kids'' mac and cheese is solid, views are great, and it''s not a zoo like the base lodges.</p>',

        -- off_mountain
        '<p>This is where Park City really shines. It''s an actual town, not just a ski base.</p>
        <h3>With Kids</h3>
        <ul>
        <li><strong>Utah Olympic Park:</strong> Bobsled rides! Your kids will talk about this forever.</li>
        <li><strong>Gorgoza Park tubing:</strong> Night tubing on Fridays is a hit.</li>
        <li><strong>Swaner Nature Preserve:</strong> Free, easy walking trails when someone needs a ski break.</li>
        </ul>
        <h3>Food</h3>
        <ul>
        <li><strong>Cafe Terigo:</strong> Great kids menu, actually good pasta for adults</li>
        <li><strong>Davanza''s:</strong> New York pizza. Kids love it. You''ll love the prices.</li>
        <li><strong>Flanagan''s:</strong> Irish pub with surprisingly good food. Live music some nights.</li>
        </ul>
        <h3>Groceries</h3>
        <p><strong>Smith''s</strong> at Kimball Junction has everything. Stop there on your way from the airport.</p>',

        -- parent_reviews_summary
        '<h3>What Parents Are Actually Saying</h3>
        <blockquote>"We''ve done Vail, Aspen, and Whistler. Park City is our favorite for the kids. Everything is just... easier."</blockquote>
        <blockquote>"Warning: it''s expensive. But ski school was worth every penny - both kids improved dramatically."</blockquote>
        <blockquote>"Main Street is walkable and fun. My teenager actually wanted to hang out with us after skiing. That''s saying something."</blockquote>
        <p><strong>The consensus:</strong> Great for families who want a full vacation experience, not just skiing. The town makes it. Budget appropriately.</p>',

        -- faqs
        '[
            {"question": "Is Park City good for beginner kids?", "answer": "Yes! Park City has excellent beginner terrain and ski school programs starting at age 3. The First Time area at the base is gentle and well-maintained. Just book ski school early during holidays - it sells out."},
            {"question": "How much does a family ski trip to Park City cost?", "answer": "Budget around $800-1200/day for a family of 4 including lift tickets, mid-range lodging, and meals. Lift tickets alone are $239/adult and $149/child. The Epic Pass saves money if you ski 3+ days."},
            {"question": "What''s the best time to visit Park City with kids?", "answer": "January offers the best powder and post-holiday value. March is great for spring skiing with fewer crowds. Avoid Presidents Week (mid-February) unless you book months ahead - it''s packed."},
            {"question": "Can you fly into Park City?", "answer": "Fly into Salt Lake City (SLC), which is only 35 minutes away - one of the shortest ski-resort transfers in the US. No mountain passes to navigate."},
            {"question": "Is Park City or Deer Valley better for families?", "answer": "Park City is better for families with varied skill levels - more terrain, more affordable, more town activities. Deer Valley is better if you have beginners only and bigger budget (no snowboarders, less crowded, more upscale)."}
        ]'::JSONB,

        -- seo_meta
        '{"title": "Park City Family Ski Guide 2024: Everything Parents Need to Know", "description": "Complete family guide to Park City ski resort. Kid-friendly terrain, costs, best times to visit, where to stay, and honest parent reviews."}'::JSONB,

        1
    );

    -- ============================================
    -- ST. ANTON CONTENT
    -- ============================================
    INSERT INTO resort_content (
        resort_id, quick_take, getting_there, where_to_stay,
        lift_tickets, on_mountain, off_mountain,
        parent_reviews_summary, faqs, seo_meta, content_version
    ) VALUES (
        st_anton_id,
        -- quick_take
        '<p>Here''s the thing about St. Anton - it''s legendary for a reason. This is where serious skiers come to play, where the apres-ski scene is borderline famous, and where the Austrian Alps deliver that "pinch me" feeling every morning.</p>
        <p>But let''s be real: this is NOT a beginner mountain. If your kids are pizza-wedging their way down greens, save St. Anton for later. If they can confidently handle blues and want to feel like they''re in a real alpine adventure? Book it.</p>
        <p><strong>The value angle:</strong> Your lift ticket here costs €72/day vs $239 at Park City. Even with flights, you might come out ahead - and the experience is completely different.</p>',

        -- getting_there
        '<p>St. Anton is in Austria''s Tyrol region, part of the legendary Ski Arlberg area (305km of connected skiing!).</p>
        <h3>Getting There</h3>
        <ul>
        <li><strong>Fly to:</strong> Innsbruck (INN) - 1.5 hours by car/train. Or Zurich (ZRH) - 2.5 hours by train.</li>
        <li><strong>Train:</strong> St. Anton has its own train station! The ÖBB Railjet from Innsbruck is scenic and stress-free. Kids love it.</li>
        <li><strong>Car rental:</strong> Nice to have but not essential. The village is walkable and lifts are everywhere.</li>
        </ul>
        <p><strong>Pro tip:</strong> Consider flying into Munich (MUC) - often cheaper flights, and the 3-hour drive through the Alps is stunning.</p>
        <p><strong>Language note:</strong> English is widely spoken in St. Anton, especially in hotels and ski schools. You''ll be fine.</p>',

        -- where_to_stay
        '<p>St. Anton village is compact and charming. Almost anywhere puts you within walking distance of lifts.</p>
        <h3>For Families</h3>
        <p><strong>Hotel Schwarzer Adler</strong> - Family-run for 450 years (!). Incredible breakfast buffet, kids'' program, and that authentic Austrian warmth. Our top pick.</p>
        <h3>Ski-In/Ski-Out</h3>
        <p><strong>Hotel Arlberg</strong> - Right at the Galzig gondola base. Pricier but you literally ski to your door.</p>
        <h3>Budget-Friendly</h3>
        <p><strong>Pension/Gasthof options</strong> - Family-run guesthouses with breakfast included. Around €100-150/night for a family room. Search "Gasthof St. Anton."</p>
        <p><strong>Real talk:</strong> Half-board (breakfast + dinner included) is common here and saves money. The hotel dinners are actually good.</p>',

        -- lift_tickets
        '<p>Here''s where St. Anton gets interesting. Your Ski Arlberg pass covers 305km of terrain across multiple villages.</p>
        <h3>Daily Rates</h3>
        <ul>
        <li>Adult: €72/day</li>
        <li>Child (2006-2017 birth year): €36/day</li>
        <li>Under 8 (with paying adult): FREE</li>
        </ul>
        <h3>Multi-Day Value</h3>
        <ul>
        <li>6-day pass: €390/adult (€65/day)</li>
        <li>6-day child: €195 (€32.50/day)</li>
        </ul>
        <p><strong>Compare that to US resorts.</strong> A family of 4 skiing 6 days: ~€1,170 total (~$1,250). At Park City? You''re looking at $4,000+ for lift tickets alone.</p>
        <p><strong>Pro tip:</strong> Buy your pass at the resort - no need to pre-book unless it''s Christmas/New Year week.</p>',

        -- on_mountain
        '<p>Let''s be honest: St. Anton is steep. But it''s also spectacular, and there IS terrain for intermediate families.</p>
        <h3>For Learning/Nervous Kids</h3>
        <p>The <strong>Gampen</strong> and <strong>Kapall</strong> areas have the gentler slopes. Ski school meets here. Don''t venture to Valluga with beginners (it''s expert only).</p>
        <h3>For Confident Kids</h3>
        <p>The <strong>Rendl</strong> area is fantastic - wide blues, great snow, and less crowded than the main mountain. Take the Rendlbahn from town.</p>
        <h3>Ski School</h3>
        <p><strong>Skischule Arlberg</strong> is the oldest ski school in Austria (founded 1901!). They know what they''re doing.</p>
        <ul>
        <li>Kids group lessons: ~€280 for 5 days (4 hours/day)</li>
        <li>English instruction available - just ask when booking</li>
        <li>KIKO club for ages 4-6 is excellent</li>
        </ul>
        <p><strong>Lunch spot:</strong> <strong>Hospiz Alm</strong> is famous, but pricey. <strong>Verwallstube</strong> has better value and still great food with views.</p>',

        -- off_mountain
        '<h3>Apres-Ski (Yes, Even With Kids)</h3>
        <p>St. Anton''s apres-ski is legendary - Mooserwirt and Krazy Kanguruh are basically ski-world famous. Here''s the thing: families go early (like 3pm), grab a table outside, have a hot chocolate and beer, enjoy the scene, and leave before it gets wild. It''s actually a fun family memory.</p>
        <h3>Evening Activities</h3>
        <ul>
        <li><strong>Night sledding:</strong> Rendl mountain offers evening sled runs. Book at the tourist office.</li>
        <li><strong>Swimming:</strong> Arlberg WellCom is a public pool/spa complex. Great for tired legs.</li>
        <li><strong>Village stroll:</strong> St. Anton''s pedestrian center is charming after dark.</li>
        </ul>
        <h3>Food</h3>
        <ul>
        <li><strong>Hazienda</strong> - Tex-Mex (kids love it, you get a break from schnitzel)</li>
        <li><strong>Bodega</strong> - Casual, good pizza and pasta</li>
        <li><strong>Museum Restaurant</strong> - Traditional Austrian, excellent Wiener Schnitzel</li>
        </ul>
        <p><strong>Grocery tip:</strong> SPAR supermarket in town has everything. Austrian chocolate for the kids is a hit.</p>',

        -- parent_reviews_summary
        '<h3>What Parents Say</h3>
        <blockquote>"We were nervous it would be too advanced, but the ski school was amazing. Both kids (8 and 11) had the best week."</blockquote>
        <blockquote>"The value compared to US resorts is unreal. We stayed 10 days for what a Colorado week costs."</blockquote>
        <blockquote>"Fair warning: if your kids can''t handle reds/blues, look elsewhere. But if they can - this is the dream."</blockquote>
        <p><strong>The consensus:</strong> Not for total beginners, but incredible value and experience for intermediate+ families. The Austrian hospitality is real.</p>',

        -- faqs
        '[
            {"question": "Is St. Anton good for beginner kids?", "answer": "Honestly? Not ideal. St. Anton is known for challenging terrain. If your kids are beginners, consider Serfaus-Fiss-Ladis or Obergurgl in Austria instead. If they can handle blue runs confidently, St. Anton becomes amazing."},
            {"question": "How much cheaper is St. Anton than US resorts?", "answer": "Significantly. A 6-day family pass (2 adults, 2 kids) costs about €1,170 (~$1,250) vs $4,000+ at major US resorts. Even with $1,500 flights, you often come out ahead and get a European adventure."},
            {"question": "Do I need to speak German in St. Anton?", "answer": "No - English is widely spoken in hotels, ski schools, and restaurants. St. Anton is very tourist-friendly. Ski school offers English instruction."},
            {"question": "Is the apres-ski scene family-friendly?", "answer": "Early afternoon (2-4pm) at places like Mooserwirt is actually fun with kids - grab an outdoor table, enjoy the music and atmosphere, then leave before evening when it gets rowdy. It''s a unique experience."},
            {"question": "What airport should I fly into for St. Anton?", "answer": "Innsbruck (INN) is closest at 1.5 hours. Zurich (ZRH) is 2.5 hours by train but often has better flight deals. Munich (MUC) is 3 hours but can be cheapest for flights from the US."}
        ]'::JSONB,

        -- seo_meta
        '{"title": "St. Anton Family Ski Guide 2024: Is It Right for Your Family?", "description": "Complete family guide to St. Anton am Arlberg, Austria. Real costs vs US resorts, terrain breakdown for kids, and honest advice on whether this legendary resort works for families."}'::JSONB,

        1
    );

    -- ============================================
    -- ZERMATT CONTENT
    -- ============================================
    INSERT INTO resort_content (
        resort_id, quick_take, getting_there, where_to_stay,
        lift_tickets, on_mountain, off_mountain,
        parent_reviews_summary, faqs, seo_meta, content_version
    ) VALUES (
        zermatt_id,
        -- quick_take
        '<p>Here''s the thing about Zermatt - you''ll see the Matterhorn and genuinely gasp. Every. Single. Morning. It''s that spectacular.</p>
        <p>This is bucket-list skiing. A car-free village where electric taxis and horse-drawn carriages are the transport. Skiing that connects to Italy (!). Snow guaranteed because the glacier means the season runs October to April.</p>
        <p>It''s expensive. Not going to pretend otherwise. But it''s also unforgettable, and the Swiss efficiency means everything just... works. Trains run on time. Lifts are immaculate. Food is excellent.</p>
        <p><strong>For families:</strong> Better than you''d think. The village is safe for kids to explore, terrain has good intermediate options, and there''s a surprising amount to do off-mountain.</p>',

        -- getting_there
        '<p>Zermatt is car-free (yes, really!). You park in Täsch and take a 12-minute shuttle train up.</p>
        <h3>Getting There</h3>
        <ul>
        <li><strong>Fly to:</strong> Geneva (GVA) - 3.5 hours by train. Or Zurich (ZRH) - 3.5 hours by train.</li>
        <li><strong>The train ride:</strong> The Glacier Express route is genuinely beautiful. Kids will be glued to the windows.</li>
        <li><strong>By car:</strong> Drive to Täsch, park at the terminal (~CHF 16/day), take the shuttle train. Easy.</li>
        </ul>
        <p><strong>Pro tip:</strong> Book Swiss rail tickets in advance for "supersaver" fares - up to 50% off. The Swiss Travel Pass is great value for families.</p>
        <p><strong>Language:</strong> German (Swiss German), but English is universally spoken in tourist areas.</p>',

        -- where_to_stay
        '<p>Zermatt is compact. Almost anywhere works. The main choice is village center (walkable to everything) or ski-in/ski-out (above town).</p>
        <h3>Family Favorite</h3>
        <p><strong>Hotel Pollux</strong> - Right in the village center, family rooms, incredible breakfast, and genuinely friendly. Great value for Zermatt.</p>
        <h3>Ski-In/Ski-Out</h3>
        <p><strong>Riffelalp Resort</strong> - At 2,222m, you take the train up to your hotel. Ski-to-door. Magical, but pricey.</p>
        <h3>Self-Catering</h3>
        <p><strong>Haus Alpine/Apartment rentals</strong> - Zermatt has excellent apartments. Cooking breakfast saves a fortune here.</p>
        <p><strong>Real talk:</strong> Half-board is less common in Zermatt than Austria, but breakfast is almost always included and worth it - Swiss breakfast buffets are amazing.</p>',

        -- lift_tickets
        '<p>Zermatt connects to Cervinia, Italy. Your pass works in both countries. Mind = blown.</p>
        <h3>Daily Rates (Zermatt-Cervinia)</h3>
        <ul>
        <li>Adult: CHF 92/day (~$105)</li>
        <li>Child (9-15): CHF 46/day</li>
        <li>Under 9: FREE with paying adult</li>
        </ul>
        <h3>Multi-Day Value</h3>
        <ul>
        <li>6-day pass: CHF 461/adult (CHF 77/day)</li>
        <li>6-day child: CHF 231</li>
        </ul>
        <p><strong>Peak Pass (International):</strong> If you''re doing multiple Swiss/French resorts, the Peak Pass can save money.</p>
        <p><strong>Pro tip:</strong> Buy your lift pass at the Zermatt Tourist Office or online - both work smoothly.</p>',

        -- on_mountain
        '<p>360km of slopes across Switzerland AND Italy. Glacier skiing means guaranteed snow. This place is ridiculous (in the best way).</p>
        <h3>For Beginners/Kids Learning</h3>
        <p>The <strong>Sunnegga-Rothorn</strong> sector has the best beginner terrain. Wide, sunny, not too crowded. The Wolli Park for kids is here.</p>
        <h3>For Intermediate Families</h3>
        <p><strong>Gornergrat</strong> - Incredible Matterhorn views, good blue/red terrain. Take the cogwheel train up (kids LOVE this train).</p>
        <p><strong>Ski to Italy:</strong> Advanced intermediates can ski down to Cervinia for lunch. Pasta in Italy, dinner back in Switzerland. Peak family vacation flex.</p>
        <h3>Ski School</h3>
        <p><strong>Zermatt Ski School</strong> offers group and private lessons in English.</p>
        <ul>
        <li>Group lessons (4-12 years): ~CHF 275 for 5 days</li>
        <li>Snowli Kids Club (3-4 years): Gentle introduction</li>
        <li>Private lessons available but expensive (~CHF 500+/day)</li>
        </ul>
        <p><strong>Lunch tip:</strong> Eat at <strong>Chez Vrony</strong> in Findeln - probably the best mountain restaurant I''ve ever been to. Book ahead. Worth every franc.</p>',

        -- off_mountain
        '<h3>The Village</h3>
        <p>Zermatt''s car-free village is genuinely magical. Kids can safely explore the pedestrian streets. Horse-drawn carriages, little shops, and the Matterhorn looming over everything.</p>
        <h3>Activities</h3>
        <ul>
        <li><strong>Gorner Gorge:</strong> A walkway through an ice-carved canyon. Free and amazing.</li>
        <li><strong>Matterhorn Museum:</strong> Underground museum about the first ascent. Surprisingly engaging for kids.</li>
        <li><strong>Swimming:</strong> Public pool with slide and Matterhorn views. Budget activity win.</li>
        </ul>
        <h3>Food</h3>
        <ul>
        <li><strong>Whymper Stube:</strong> Raclette and fondue in a cozy setting. Classic Swiss.</li>
        <li><strong>Brown Cow Pub:</strong> Burgers and casual food. Kids menu.</li>
        <li><strong>Migros/Coop:</strong> Supermarkets for self-catering essentials.</li>
        </ul>
        <p><strong>Budget tip:</strong> A cheese fondue at a grocery-store restaurant (yes, that''s a thing in Switzerland) is like CHF 15 vs CHF 40 at a proper restaurant.</p>',

        -- parent_reviews_summary
        '<h3>What Parents Say</h3>
        <blockquote>"The moment my kids saw the Matterhorn, I knew it was worth every penny. That mountain is UNREAL in person."</blockquote>
        <blockquote>"It''s expensive but actually felt worth it. Everything works perfectly - Swiss efficiency is real."</blockquote>
        <blockquote>"We skied to Italy for lunch. MY KIDS SKIED TO ANOTHER COUNTRY. That''s the trip they''ll remember forever."</blockquote>
        <p><strong>The consensus:</strong> Expensive but legitimately special. Save up, go once, create memories that last forever. The car-free village is a huge family bonus.</p>',

        -- faqs
        '[
            {"question": "Is Zermatt too expensive for families?", "answer": "It''s definitely premium - budget CHF 800-1200/day for a family of 4 including lift tickets, mid-range lodging, and meals. BUT: kids under 9 ski free, apartments with kitchens reduce food costs, and the experience is genuinely bucket-list level."},
            {"question": "Can you really ski to Italy from Zermatt?", "answer": "Yes! Your lift pass covers both Zermatt (Switzerland) and Cervinia (Italy). Confident intermediate skiers can ski down to Italy for lunch and back. It''s incredible."},
            {"question": "How does the car-free village work with kids?", "answer": "It''s actually perfect for families. Kids can run around safely without traffic. Electric taxis and buses handle luggage transfers. Most hotels will pick you up from the train station."},
            {"question": "When is the best time to ski Zermatt with family?", "answer": "January and March offer the best balance of snow, weather, and value. The glacier means snow is guaranteed all season. Avoid Christmas/New Year (prices spike) and Swiss school holidays (February) if possible."},
            {"question": "Is Zermatt good for beginner kids?", "answer": "Reasonably good. The Sunnegga area has gentle terrain and the Wolli Kids Club is excellent. Not AS beginner-friendly as some resorts, but better than its expert reputation suggests."}
        ]'::JSONB,

        -- seo_meta
        '{"title": "Zermatt Family Ski Guide 2024: Is It Worth the Splurge?", "description": "Complete family guide to Zermatt, Switzerland. Honest costs, kid-friendly terrain, skiing to Italy, and whether this bucket-list resort works for families."}'::JSONB,

        1
    );

END $$;

"""
Regression tests built from the contradictions found on the live page (1 Nov 2026).
Run:  cd <project> && python -m unittest discover -s tests -v
(or pytest - the tests are plain unittest.TestCase)
"""
import copy, datetime, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.dirname(HERE)]

import analytics_engine as ae
import driver_engine as de
import narrative_generator as ng
from fixtures import snapshot, NEWS

WIB = de.WIB
CAUSAL = ("dipicu", "didorong", "akibat ", "disebabkan", "memicu", "menyedot", "foreign outflow")


def build(snap):
    ews = ae.evaluate_ews(snap)
    regime = ae.classify_macro_regime(snap, ews)
    md = ae.analyze_market_drivers(snap, regime, ews)
    indo = ae.analyze_indonesia_macro_sentiment(snap, ews, regime)
    sectors = ae.compute_sector_scorecard(snap, regime)
    return ews, regime, md, indo, sectors


class Drivers(unittest.TestCase):
    def setUp(self):
        self.snap = snapshot()
        self.ews, self.regime, self.md, self.indo, self.sectors = build(self.snap)

    def test_no_causal_claims_in_any_driver_text(self):
        for k, v in self.md.items():
            text = (v.get("driver") or "").lower()
            for w in CAUSAL:
                self.assertNotIn(w, text, f"{k}: '{w}' asserts a cause the data cannot prove")

    def test_btc_up_is_never_called_koreksi(self):          # was: 'Koreksi Bitcoin ... (1D: +0.52%)'
        d = self.md["crypto"]["driver"].lower()
        self.assertNotIn("koreksi", d)
        self.assertEqual(self.md["crypto"]["state"], "datar")
        self.assertIn("20d", d)                              # the negative 20D trend is still shown

    def test_oil_up_does_not_show_an_oil_price_drop_headline(self):
        self.assertNotIn("Oil Price Drop", self.md["oil"]["driver"])
        self.assertNotIn("Oil Price Drop", self.md["oil"]["news"]["title"])

    def test_gold_does_not_blame_yields_when_yields_fell(self):
        d = self.md["gold"]["driver"].lower()
        self.assertNotIn("yield tinggi", d)
        self.assertNotIn("tingginya yield", d)
        self.assertNotIn("dolar kuat", d)

    def test_noise_headlines_are_filtered(self):
        for cat, kind in (("crypto", "crypto"), ("dollar", "dollar")):
            titles = [i["title"] for i in de.pick_news(NEWS[cat], kind, None, limit=10)]
            for t in titles:
                self.assertNotIn("Live Price", t)
                self.assertNotIn("BITSTAMP", t)
                self.assertTrue(de._mostly_latin(t))

    def test_same_event_headlines_are_deduplicated(self):
        picks = de.pick_news(NEWS["crypto"], "crypto", None, limit=5)
        self.assertEqual(len(picks), 1, [p["title"] for p in picks])

    def test_indonesia_headline_must_match_the_asset(self):
        t = self.md["indonesia"]["news"]["title"]
        self.assertNotIn("QRIS", t)

    def test_tone_rule_blocks_contradicting_headline(self):
        items = [{"title": "Oil price drop deepens as OPEC supply glut widens", "source": "X"}]
        self.assertEqual(de.pick_news(items, "oil", "naik"), [])
        self.assertEqual(len(de.pick_news(items, "oil", "turun")), 1)


class Indonesia(unittest.TestCase):
    def test_single_usdidr_value_everywhere(self):         # was: 18,120 on cards vs 18,140 in the driver text
        snap = snapshot()
        ews, regime, md, indo, sectors = build(snap)
        msg = ng.generate_whatsapp_broadcast(snap, ews, regime, [], sectors, [], 0.029, indo, None, None, md)
        self.assertEqual(indo["usdidr_val"], 18120)
        self.assertIn("18,120", msg)
        self.assertNotIn("18,140", msg + md["indonesia"]["driver"])

    def test_alias_ticker_is_resolved_not_replaced_by_a_constant(self):
        snap = snapshot()
        snap["prices"]["IDR=X"] = snap["prices"].pop("USDIDR=X")
        snap["prices"]["IDR=X"]["close"] = 18077
        _, _, md, indo, _ = build(snap)
        self.assertEqual(indo["usdidr_val"], 18077)
        self.assertIn("18,077", md["indonesia"]["driver"])

    def test_deep_20d_drop_is_not_called_konsolidasi(self):
        _, _, md, indo, _ = build(snapshot())
        self.assertEqual(indo["ihsg_status"], "KOREKSI DALAM (20D)")
        self.assertIn("20D", md["indonesia"]["driver"])

    def test_no_invented_bi_or_foreign_flow_claims(self):
        _, _, md, indo, _ = build(snapshot())
        blob = (indo["summary"] + indo["bi_desc"] + md["indonesia"]["driver"]).lower()
        for w in ("dipaksa", "foreign outflow", "triple intervention", "tergerus"):
            self.assertNotIn(w, blob)
        self.assertIn("estimasi", indo["bi_status"].lower())

    def test_eido_label_comes_from_eido_not_ihsg(self):
        snap = snapshot()
        snap["prices"]["EIDO"]["change_1d_pct"] = 1.5
        _, _, _, indo, _ = build(snap)
        self.assertEqual(indo["eido_status"], "MENGUAT")


class MissingData(unittest.TestCase):
    def test_missing_inputs_are_reported_not_invented(self):
        snap = snapshot()
        del snap["prices"]["BTC-USD"]; del snap["prices"]["USDIDR=X"]; del snap["prices"]["EIDO"]
        ews, regime, md, indo, sectors = build(snap)
        msg = ng.generate_whatsapp_broadcast(snap, ews, regime, [], sectors, [], 0, indo, None, None, md)
        self.assertIn("data tidak tersedia", msg.lower())
        self.assertIsNone(indo["usdidr_val"])
        self.assertNotIn("Rp 18", msg)
        self.assertNotIn("US$ 0 ", msg)
        self.assertEqual(ews[[s["name"] for s in ews].index("USD / IDR (Kurs Rupiah)")]["status"], "N/A")

    def test_regime_is_not_forced_when_inputs_missing(self):    # was: silent catch-all -> DEFLASI_KONTRAKSI
        snap = snapshot(); del snap["prices"]["CL=F"]
        ews = ae.evaluate_ews(snap)
        self.assertEqual(ae.classify_macro_regime(snap, ews)["regime_id"], "DATA_TIDAK_LENGKAP")

    def test_no_fabricated_headline_or_source_when_feed_is_empty(self):
        snap = snapshot(); snap["news_by_category"] = {}; snap["crypto_news"] = []
        ews, regime, md, indo, sectors = build(snap)
        for k in ("gold", "oil", "crypto", "dollar", "tech", "indonesia"):
            self.assertFalse(md[k]["news"]["available"])
            self.assertNotIn("Reuters", md[k]["driver"])
        msg = ng.generate_whatsapp_broadcast(snap, ews, regime, [], sectors, [], 0.029, indo, None, None, md)
        self.assertIn("tidak ada berita kripto relevan", msg)

    def test_missing_irx_does_not_fabricate_a_curve(self):
        snap = snapshot(); del snap["prices"]["^IRX"]
        ews = ae.evaluate_ews(snap)
        curve = [s for s in ews if s["name"].startswith("Yield Curve")][0]
        self.assertEqual(curve["status"], "N/A")


class RegimeAndEws(unittest.TestCase):
    def test_regime_text_matches_what_the_code_does(self):
        snap = snapshot()
        ews = ae.evaluate_ews(snap)
        regime = ae.classify_macro_regime(snap, ews)
        self.assertEqual(regime["regime_id"], "STAGFLASI")
        text = ae.explain_regime_exit(snap, ews)
        self.assertIn("REFLASI", text)                       # both single-threshold exits land here
        self.assertIn("TIDAK memakai data pertumbuhan", text)
        self.assertNotIn("Goldilocks", text)
        # the old claim "need oil < 80 AND yield < 4.40%" must be false in code:
        s2 = copy.deepcopy(snap); s2["prices"]["CL=F"]["close"] = 87.9
        self.assertNotEqual(ae.classify_macro_regime(s2, ews)["regime_id"], "STAGFLASI")

    def test_xlf_is_not_labelled_defensive(self):
        snap = snapshot()
        ews = ae.evaluate_ews(snap); regime = ae.classify_macro_regime(snap, ews)
        rows = {s["ticker"]: s for s in ae.compute_sector_scorecard(snap, regime)}
        self.assertNotIn("Defensif", rows["XLF"]["rationale"])
        self.assertIn("Defensif", rows["XLV"]["rationale"])

    def test_gold_ews_has_no_absolute_price_threshold(self):
        ews = ae.evaluate_ews(snapshot())
        gold = [s for s in ews if s["name"].startswith("Emas")][0]
        self.assertEqual(gold["status"], "AMAN")
        self.assertNotIn("de-dolarisasi", gold["context"])

    def test_curve_status_does_not_depend_on_10y_level(self):
        snap = snapshot()
        curve = [s for s in ae.evaluate_ews(snap) if s["name"].startswith("Yield Curve")][0]
        self.assertEqual(curve["status"], "AMAN")            # +95.6 bps; was WASPADA only because 10Y > 4.5

    def test_liquidity_rule_is_shared_by_ews_and_broadcast(self):
        snap = snapshot()
        ews, regime, md, indo, sectors = build(snap)
        liq = [s for s in ews if s["name"].startswith("Fed Net Liquidity")][0]
        label, status = de.liquidity_state(5741.5, -52.5)
        self.assertEqual(liq["status"], status)
        msg = ng.generate_whatsapp_broadcast(snap, ews, regime, [], sectors, [], 0.029, indo, None, None, md)
        self.assertIn(label, msg)
        self.assertNotIn("Agresif", msg)


class Chain(unittest.TestCase):
    def test_chain_title_and_text_cannot_disagree(self):
        snap = snapshot(); _, _, md, _, sectors = build(snap)
        chain = ng.build_validated_sentiment_chain(snap["prices"], sectors, snap, md)
        self.assertIn("Bitcoin bergerak datar", chain)
        self.assertNotIn("Likuidasi", chain)
        self.assertNotIn("Sektor Defensif", chain)
        self.assertIn("Sektor Terkuat: XLE", chain)

    def test_up_move_never_uses_down_words(self):
        snap = snapshot()
        for t in ("SPY", "QQQ"):
            snap["prices"][t]["change_1d_pct"] = 1.2
        _, _, md, _, sectors = build(snap)
        chain = ng.build_validated_sentiment_chain(snap["prices"], sectors, snap, md)
        self.assertIn("Ekuitas AS naik", chain)
        self.assertNotIn("terkoreksi", chain.lower())


class TimeLabels(unittest.TestCase):
    def test_sunday_broadcast_is_dated_to_friday_session(self):     # was: "Update Perdagangan: Minggu"
        now = datetime.datetime(2026, 11, 1, 20, 6, tzinfo=WIB)
        self.assertEqual(de.last_us_session_date(now), datetime.date(2026, 10, 30))
        self.assertEqual(de.fmt_id_date(de.last_us_session_date(now)), "Jumat, 30 Oktober 2026")

    def test_session_rolls_forward_after_the_close(self):
        # Tue 06:00 WIB = Mon 18:00 New York (after the 16:00 close)
        now = datetime.datetime(2026, 11, 3, 6, 0, tzinfo=WIB)
        self.assertEqual(de.last_us_session_date(now), datetime.date(2026, 11, 2))

    def test_h41_follows_dst(self):                                  # was: hard-coded "Jumat ~03:30 WIB"
        winter = de.h41_release_text(datetime.datetime(2026, 11, 1, 20, 6, tzinfo=WIB))
        summer = de.h41_release_text(datetime.datetime(2026, 7, 1, 12, 0, tzinfo=WIB))
        self.assertIn("Jumat ~04:30 WIB", winter)
        self.assertIn("Jumat ~03:30 WIB", summer)

    def test_broadcast_has_no_hardcoded_h41_time(self):
        snap = snapshot(); ews, regime, md, indo, sectors = build(snap)
        msg = ng.generate_whatsapp_broadcast(snap, ews, regime, [], sectors, [], 0.029, indo, None, None, md)
        self.assertNotIn("Update Perdagangan", msg)
        self.assertIn("Penutupan Wall Street:", msg)


if __name__ == "__main__":
    unittest.main()

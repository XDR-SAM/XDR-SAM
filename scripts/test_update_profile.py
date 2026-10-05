from datetime import date
import unittest
from update_profile import streaks, CalendarParser, markdown

class ProfileTests(unittest.TestCase):
    def test_unfinished_today_preserves_streak(self):
        self.assertEqual(streaks([{'date':'2026-10-04','count':2},{'date':'2026-10-05','count':1},{'date':'2026-10-06','count':0}],date(2026,10,6)),(2,2))
    def test_gap_breaks_streak(self):
        self.assertEqual(streaks([{'date':'2026-10-01','count':2},{'date':'2026-10-03','count':1}],date(2026,10,6)),(0,1))
    def test_future_days_do_not_count(self):
        self.assertEqual(streaks([{'date':'2026-10-06','count':1},{'date':'2026-10-07','count':1}],date(2026,10,6)),(1,1))
    def test_empty(self):
        self.assertEqual(streaks([],date(2026,10,6)),(0,0))
    def test_calendar_counts(self):
        p=CalendarParser()
        p.feed('<td id="a" data-date="2026-10-05" data-level="4"></td><tool-tip for="a">1,234 contributions on October 5th.</tool-tip>')
        self.assertEqual(p.counts['a'],1234)
    def test_repository_text_is_escaped(self):
        self.assertEqual(markdown('<b>a|b</b>\n[x]'),'&lt;b&gt;a\\|b&lt;/b&gt; \\[x\\]')

if __name__=='__main__':
    unittest.main()

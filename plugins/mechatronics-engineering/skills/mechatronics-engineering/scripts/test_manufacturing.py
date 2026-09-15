import unittest
from manufacturing_calcs import mmc, little_lead_time, kingman_wait, kanban_cards, capability, zero_failure_upper_bound


class ManufacturingTests(unittest.TestCase):
    def test_mm1_and_little(self):
        q=mmc(6,8)
        self.assertAlmostEqual(q['utilisation'],.75)
        self.assertAlmostEqual(q['mean_queue_wait_h'],.375)
        self.assertAlmostEqual(q['mean_system_time_h'],.5)
        self.assertAlmostEqual(q['mean_system_items'],3)
        self.assertAlmostEqual(little_lead_time(q['mean_system_items'],6),q['mean_system_time_h'])

    def test_mmc_known_erlang_c(self):
        q=mmc(10,6,2)
        self.assertAlmostEqual(q['probability_wait'],25/33)
        self.assertAlmostEqual(q['mean_queue_wait_h'],25/66)
        self.assertAlmostEqual(q['mean_system_items'],60/11)
        self.assertLess(mmc(6,8,2)['mean_queue_wait_h'],mmc(6,8,1)['mean_queue_wait_h'])

    def test_zero_arrivals_and_unstable_queues(self):
        q=mmc(0,8,2)
        self.assertEqual(q['mean_queue_wait_h'],0)
        self.assertAlmostEqual(q['mean_system_time_h'],1/8)
        for f,args in ((mmc,(8,8,1)),(mmc,(20,8,2)),(kingman_wait,(8,.125,1,1)),(mmc,(1,8,1.5))):
            with self.assertRaises(ValueError): f(*args)

    def test_kingman_reduces_to_mm1(self):
        self.assertAlmostEqual(kingman_wait(6,.125,1,1),mmc(6,8)['mean_queue_wait_h'])
        self.assertAlmostEqual(kingman_wait(6,.125,1,.5),.234375)

    def test_kanban_rounding_and_sensitivity(self):
        self.assertEqual(kanban_cards(12,1.5,6,.2),4)
        self.assertGreater(kanban_cards(12,3,6,.2),4)
        with self.assertRaises(ValueError): kanban_cards(12,1.5,0,.2)

    def test_capability_centering(self):
        q=capability(9.8,10.2,10.05,.04)
        self.assertAlmostEqual(q['cp'],5/3)
        self.assertAlmostEqual(q['cpk'],1.25)
        centered=capability(9.8,10.2,10,.04)
        self.assertAlmostEqual(centered['cp'],centered['cpk'])

    def test_zero_failure_bound(self):
        self.assertAlmostEqual(zero_failure_upper_bound(10),1-.05**.1)
        self.assertGreater(zero_failure_upper_bound(10),.25)
        self.assertLess(zero_failure_upper_bound(59),.05)
        with self.assertRaises(ValueError): zero_failure_upper_bound(0)


if __name__=='__main__': unittest.main()

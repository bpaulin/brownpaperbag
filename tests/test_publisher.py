import unittest
from brownpaperbag.publisher import split_message, message_to_topic_and_value


class SplitMessageTestCase(unittest.TestCase):
    def test_split_message_simple(self):
        self.assertEqual(
            split_message('*1*0*0012##'),
            ['*1*0*0012##']
        )

    def test_split_message_several(self):
        self.assertEqual(
            split_message('*1*0*0012##*1*0*0011##'),
            ['*1*0*0012##', '*1*0*0011##']
        )

    def test_split_message_wrong(self):
        self.assertEqual(
            split_message('DA FUCK ??!!'),
            []
        )

    def test_split_message_energy(self):
        self.assertEqual(
            split_message('*#18*51*113*0##'),
            ['*#18*51*113*0##']
        )


class MessageToTopicTestCase(unittest.TestCase):

    def test_message_to_topic_and_value_light(self):
        self.assertEqual(
            message_to_topic_and_value('*1*0*0012##'),
            {'topic': '/1/0012', 'payload': '0'}
        )

    def test_message_to_topic_and_value_automation(self):
        self.assertEqual(
            message_to_topic_and_value('*2*2*0012##'),
            {'topic': '/2/0012', 'payload': '2'}
        )

    def test_message_to_topic_and_value_energy(self):
        self.assertEqual(
            message_to_topic_and_value('*#18*51*113*23##'),
            {'topic': '/18/51', 'payload': '23'}
        )

    def test_message_to_topic_and_value_wrong(self):
        self.assertFalse(
            message_to_topic_and_value('DA FUCK')
        )


if __name__ == '__main__':
    unittest.main()

"""import unittest
import json
import os


from bs4 import BeautifulSoup
import parsing.drom_parser as drom_parser


class TestDromParser(unittest.TestCase):
    def test_correct_url(self):
        correct_url = "https://auto.drom.ru/audi/"
        parser = drom_parser.SyncDromParser()
        parser.load_html(correct_url)
        self.assertEqual(parser.page.status_code, 200)

    def test_get_html_with_blocked_url(self):
        blocked_url = "https://www.avito.ru/"
        with self.assertRaises(ValueError):
            parser = drom_parser.SyncDromParser()
            parser.load_html(blocked_url)
            self.assertEqual(parser.page.status_code, 403)

    async def test_async_get_html_by_correct_url(self):
        correct_url = "https://auto.drom.ru/audi/"
        parser = drom_parser.AsyncDromParser()
        await parser.load_html(correct_url)
        print(parser.page.status)
        self.assertEqual(parser.page.status, 200)

    async def test_async_get_html_by_blocked_url(self):
        blocked_url = "https://www.avito.ru/"
        with self.assertRaises(ValueError):
            parser = drom_parser.AsyncDromParser()
            await parser.load_html(blocked_url)
            self.assertEqual(parser.page.status, 403)

    def test_parsing(self):
        filename = "audi_a4"
        parser = drom_parser.SyncDromParser()
        with open(os.path.join("test_html", f"{filename}.html"), "r") as f:
            parser.page = f.read()
            parser.soup = BeautifulSoup(parser.page, "html.parser")
        drom_parser.BaseDromParser.parse(parser, "https://auto.drom.ru/")
        with open(os.path.join("json_answer", f"{filename}.json"), 'r') as file:
            deserialized_result = json.load(file)
        self.assertEqual(parser.resulting_dicts, deserialized_result)


if __name__ == '__main__':
    unittest.main()
"""
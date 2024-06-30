import re
import abc
import aiohttp
import requests
import colorama
from bs4 import BeautifulSoup


colorama.init()


class HtmlLoadError(Exception):
    def __init__(self, message, value):
        self.value = value
        super().__init__(message)


class BaseDromParser(metaclass=abc.ABCMeta):
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.headers = None
        self.url_to_parse = None
        self.page = None
        self.soup = None
        self.resulting_dicts = []

    @abc.abstractmethod
    def load_html(self, url):
        pass

    def set_debug_mode(self, on: bool):
        self.debug_mode = on

    def _get_car_ids(self):
        self.car_hrefs = [el.get("href") for el in self.soup.find_all("a", class_="css-4zflqt e1huvdhj1")]
        if len(self.car_hrefs) != 0:
            print(self.car_hrefs) if self.debug_mode else ...
        else:
            print(colorama.Fore.RED + "not found car_hrefs")
            print(colorama.Style.RESET_ALL)  # Сброс цветовых настроек
            return None
        self.car_ids = [int(el.split('/')[-1].split('.')[0]) for el in self.car_hrefs]
        return 0

    def _get_car_names_and_years(self):
        self.car_names_and_years = [el.text for el in self.soup.find_all("div", class_="css-16kqa8y e3f4v4l2")]
        if len(self.car_names_and_years) != 0:
            print(self.car_names_and_years) if self.debug_mode else ...
            return 0
        print(colorama.Fore.RED + "not found car_names_and_years" + colorama.Style.RESET_ALL)
        return None

    def _get_car_specifications(self):
        spec = [el.text for el in self.soup.find_all("span", class_="css-1l9tp44 e162wx9x0")]
        print(spec) if self.debug_mode else ...
        self.car_specifications = [[spec[i + j] for i in range(5)] for j in range(0, len(spec) - 6, 5)]
        if len(self.car_specifications) != 0:
            print(self.car_specifications) if self.debug_mode else ...
            return 0
        print(colorama.Fore.RED + "not found car_engine_specifications" + colorama.Style.RESET_ALL)
        return None

    def _get_car_prices(self):
        car_prices = [el.text for el in self.soup.find_all("span", class_="css-46itwz e162wx9x0")]
        self.car_prices = [int(''.join([sym for sym in word if sym.isdigit()])) for word in car_prices]
        if len(self.car_prices) != 0:
            print(self.car_prices) if self.debug_mode else ...
            return 0
        print(colorama.Fore.RED + "not found car_prices" + colorama.Style.RESET_ALL)
        return None

    def format_data(self):
        if not (len(self.car_names_and_years)
                == len(self.car_prices)
                == len(self.car_ids)
                == len(self.car_hrefs)
                == len(self.car_specifications)):
            print(colorama.Fore.RED + "parsing fault occured: number of features doesn'match with number of cars")
            print(colorama.Style.RESET_ALL)  # Сброс цветовых настроек
            return None

        for i in range(len(self.car_ids)):
            brand_model, year = self.car_names_and_years[i].split(', ')
            engine_volume, engine_power = re.findall(r'\d+\.\d+|\d+', self.car_specifications[i][0])
            self.resulting_dicts.append(
                {"car_id": self.car_ids[i],
                 "href": self.car_hrefs[i],
                 "brand_model": brand_model, "production_year": int(year),
                 "price": self.car_prices[i],
                 "volume": float(engine_volume),
                 "power": int(engine_power),
                 "gearbox_type": self.car_specifications[i][2].replace(',', ''),
                 # "wheel drive": int(self.car_specifications[i][3][0]),
                 "mileage": int(self.car_specifications[i][4].replace(' ', '').replace('км', ''))}
            )
        print(self.resulting_dicts) if self.debug_mode else ...
        return 0

    def parse(self, change_url_to_parse):
        try:
            if (
                    self._get_car_ids() is None or
                    self._get_car_names_and_years() is None or
                    self._get_car_specifications() is None or
                    self._get_car_prices() is None or
                    self.format_data() is None
            ):
                return None

            print(colorama.Fore.GREEN + "page parsed successfully" + colorama.Style.RESET_ALL)
            return self.resulting_dicts
        except IndexError:
            print(colorama.Fore.RED + "Index error" + colorama.Style.RESET_ALL)
            return None
        except ValueError:
            print(colorama.Fore.RED + "Value error" + colorama.Style.RESET_ALL)
            return None


class SyncDromParser(BaseDromParser):
    def load_html(self, url):
        self.url_to_parse = url
        self.page = requests.get(self.url_to_parse, headers=self.headers)
        if self.page.status_code != 200:
            raise ValueError(f"Failed to get data from given url, error: {self.page.status_code}")
        self.soup = BeautifulSoup(self.page.text, "html.parser")

    def parse(self, change_url_to_parse):
        self.load_html(change_url_to_parse)
        super().parse(change_url_to_parse)


class AsyncDromParser(BaseDromParser):
    async def load_html(self, url):
        self.url_to_parse = url
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url_to_parse, headers=self.headers) as page:
                self.page = page
                if page.status != 200:
                    raise HtmlLoadError(f"Failed to get data from the URL, error: {page.status}", page.status)
                html = await page.text()
                self.soup = BeautifulSoup(html, "html.parser")

    async def parse(self, change_url_to_parse):
        try:
            await self.load_html(change_url_to_parse)
            super().parse(change_url_to_parse)
        except HtmlLoadError as err:
            if err.value != 503:
                raise err
            print(err)



async def parse_page(db_config: dict, parse_config: dict, page: int):
    _parser = AsyncDromParser()
    await _parser.parse(
        f"{parse_config['home_url']}/{parse_config['car_brand']}/page{page}/{parse_config['settings_url']}"
    )
    print(page)
    if _parser.resulting_dicts is None:
        return None
    return _parser.resulting_dicts

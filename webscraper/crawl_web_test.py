import unittest

from main import crawl_website
class CrawlWebsiteTestCase(unittest.TestCase):
    def test_crawl_website(self):
        urls = [
            "https://www.fullerton.edu/ecs/cs/admission/graduateadmission.php",
            "https://www.fullerton.edu/ecs/cs/resources/advisement.php",
            "https://www.fullerton.edu/ecs/cs/resources/organizations.php",
            "https://www.fullerton.edu/ecs/cs/about/capstone.html"

        ]

        result = crawl_website("https://www.fullerton.edu/ecs/cs")
        missing_urls = set(urls) - result

        self.assertFalse(missing_urls, f"Missing URLs: {', '.join(missing_urls)}")
        self.assertSetEqual(set(urls).intersection(result), set(urls), "Test case failed")



if __name__ == "__main__":
    unittest.main()
    ##
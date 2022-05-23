import logging
import os

import click

from dpma_crawler.dpma_extractor import DpmaExtractor

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


@click.command()
# @click.option("-i", "--id", "rb_id", type=int, help="The rb_id to initialize the crawl from")
# @click.option("-s", "--state", type=click.Choice(State), help="The state ISO code")
@click.option('-p', '--path', type=click.Path(), help="The path to the csv file including company names to be crawled.")
def run(path): #rb_id: int, state: State
    # if state == State.SCHLESWIG_HOLSTEIN:
    #     if rb_id < 7830:
    #         error = ValueError("The start rb_id for the state SCHLESWIG_HOLSTEIN (sh) is 7831")
    #         log.error(error)
    #         exit(1)
    DpmaExtractor().extract()


if __name__ == "__main__":
    run()

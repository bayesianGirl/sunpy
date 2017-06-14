"""
This module implements SWAPClient
"""
# This module was developed with funding provided by
# the Google Summer of Code 2016.

__author__ = "Sudarshan Konge"
__email__ = "sudk1896@gmail.com"

import datetime

from sunpy.net.dataretriever.client import GenericClient
from sunpy.util.scraper import Scraper

__all__ = ['SWAPClient']


class SWAPClient(GenericClient):
    """
    Returns a list of URLS to PROBA2 SWAP [1] files corresponding to value of
    input timerange. URL source: `http://proba2.oma.be/swap/data/`.

    Parameters
    ----------
    timerange : `sunpy.time.TimeRange`
        Time range for which data is to be downloaded.
        Example value - TimeRange('2015-12-30 00:00:00','2015-12-31 00:01:00')

    Instrument : Fixed argument with value 'swap'

    Level : 0, 1, 'q' or 'Q' as arguments.
        Data processing level as described by SWAP - see reference [2].

    Returns
    -------
    urls : list
        list of urls corresponding to requested time range.

    Examples
    --------
    >>> from sunpy.net import Fido
    >>> from sunpy.net import attrs as a

    >>> results = Fido.search(a.Time('2015/12/28 00:00:00', '2015/12/28 00:03:00'), a.Instrument('swap'), a.Level(1))
    >>> print(results)
    >>> [<Table length=2>
         Start Time           End Time      Source Instrument
           str19               str19         str6     str4
    ------------------- ------------------- ------ ----------
    2015-12-28 00:00:00 2015-12-29 00:00:00 Proba2       swap
    2015-12-29 00:00:00 2015-12-30 00:00:00 Proba2       swap]

    >>> response = Fido.fetch(results)

    References
    ----------
    [1] http://proba2.sidc.be/about/SWAP
    [2] http://proba2.sidc.be/data/SWAP

    """

    def _get_url_for_timerange(self, timerange, **kwargs):
        """
        Returns list of urls corresponding to given TimeRange.  The level
        dependent start dates are taken from the SWAP website.
        """
        level = kwargs.get('level', 1)
        if level == 1 or level == 0:
            SWAP_STARTDATE = datetime.datetime(2009, 11, 24)
        else:
            SWAP_STARTDATE = datetime.datetime(2010, 1, 4)
        if timerange.start < SWAP_STARTDATE:
            raise ValueError('Earliest date for which SWAP data is available is {:%Y-%m-%d}'.format(SWAP_STARTDATE))
        datatype = {0: 'eng', 1: 'bsd', 'q': 'qlk', 'Q': 'qlk'}
        prefix = 'http://proba2.oma.be/swap/data/{datatype}/%Y/%m/%d/'
        if level == 0 or level == 1:
            suffix = '{instrument}_lv{level}_%Y%m%d_%H%M%S.fits'
        else:
            suffix = '%Y_%m_%d__%H_%M_%S__PROBA2_SWAP_SWAP_174.jp2'
        url_pattern = prefix + suffix
        crawler = Scraper(url_pattern, instrument='swap', level=level, datatype=datatype[level])
        if not timerange:
            return []
        result = crawler.filelist(timerange)
        return result

    def _makeimap(self):
        """
        Helper Function:used to hold information about source.
        """
        self.map_['source'] = 'PROBA2'
        self.map_['instrument'] = 'SWAP'
        self.map_['phyobs'] = 'irradiance'
        self.map_['provider'] = 'ESA'
        self.map_['wavelength'] = '174 Angstrom'

    @classmethod
    def _can_handle_query(cls, *query):
        """
        Answers whether client can service the query.

        Parameters
        ----------
        query : list of query objects

        Returns
        -------
        boolean : answer as to whether client can service the query

        """
        chk_var = 0
        for x in query:
            if x.__class__.__name__ == 'Instrument' and type(x.value) is str and x.value.lower() == 'swap':
                chk_var += 1
            if x.__class__.__name__ == 'Level' and x.value in (0, 1, 'q', 'Q'):
                chk_var += 1
        return chk_var == 2

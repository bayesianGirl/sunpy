#This module was developed with funding provided by
#the Google Summer of Code 2016.

__author__ = "Sudarshan Konge"
__email__ = "sudk1896@gmail.com"

import datetime
import urllib2


from sunpy.net.dataretriever.client import GenericClient
from sunpy.util.scraper import Scraper

from sunpy.time import TimeRange

__all__ = ['SWAPClient']

class SWAPClient(GenericClient):
    """
    Returns a list of URLS to Proba2 SWAP files corresponding to value of input timerange.
    URL source: `http://proba2.oma.be/swap/data/bsd/`.

    The earliest date available is from 24-Nov-2009

    Parameters
    ----------
    timerange: sunpy.time.TimeRange
        time range for which data is to be downloaded.
        Example value - TimeRange('2015-12-30 00:00:00','2015-12-31 00:01:00')
    
    Instrument: Fixed argument = 'swap'

    Level: Level can take only 0 and 1 as arguments.

    Returns
    -------
    urls: list
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
    """
    
    def _get_url_for_timerange(self, timerange, **kwargs):
        """
        returns list of urls corresponding to given TimeRange.
        """
        level = kwargs.get('level', 1)
        SWAP_STARTDATE = datetime.datetime(2009, 11, 24)
        if timerange.start < SWAP_STARTDATE:
            raise ValueError('Earliest date for which SWAP data is available is '+ str(SWAP_STARTDATE))
        datatype = {0: 'eng', 1:'bsd'}
        prefix = 'http://proba2.oma.be/swap/data/{datatype}/'
        suffix = '%Y/%m/%d/{instrument}_lv{level}_%Y%m%d_%H%M%S.fits'
        url_pattern = prefix + suffix
        crawler = Scraper(url_pattern, instrument= 'swap', level = level, datatype = datatype[level])
        if not timerange:
            return []
        result = crawler.filelist(timerange)
        return result

    def _makeimap(self):
        """
        Helper Function:used to hold information about source.
        """
        self.map_['source'] = 'Proba2'
        self.map_['instrument'] = 'swap'
        self.map_['phyobs'] = 'irradiance'
        self.map_['provider'] = 'esa'
        self.map_['wavelength'] = '174 AA'

    @classmethod
    def _can_handle_query(cls, *query):
        """
        Answers whether client can service the query.
        
        Parameters
        ----------
        query : list of query objects
        
        Returns
        -------
        boolean: answer as to whether client can service the query
        
        """
        chkattr = ['Time', 'Instrument', 'Level']
        chklist = [x.__class__.__name__ in chkattr for x in query]
        chk_var = 0
        for x in query:
            if x.__class__.__name__ == 'Instrument' and x.value.lower() == 'swap':
                chk_var += 1
            if x.__class__.__name__ == 'Level' and x.value in (0,1):
                chk_var += 1
        if (chk_var == 2):
            return True
        return False
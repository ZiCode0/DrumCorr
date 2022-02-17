import obspy.clients.fdsn.header

from lib import fdsn
from obspy.clients.fdsn import Client
from obspy import Trace


def remove_response(trace: Trace, fdsn_url: str) -> bool:
    """
    Remove response using FDSN server
    :param trace: target trace to remove response
    :param fdsn_url: target fdsn server url
    :return: Response answer of success as bool
    """
    # init on first run
    if not fdsn.fdsn_client:
        fdsn.fdsn_client = Client(fdsn_url)

    try:
        # get inventory
        inventory = fdsn.get_inventory(network=trace.stats.network,
                                       station=trace.stats.station,
                                       location=trace.stats.location,
                                       channel=trace.stats.channel,
                                       start_time=trace.stats.starttime,
                                       end_time=trace.stats.endtime
                                       )
        # remove response
        trace.remove_response(inventory=inventory)
        # return remove_response result as bool answer
        return True
    # data not found: 204
    except obspy.clients.fdsn.header.FDSNNoDataException:
        # return remove_response result as bool answer
        return False

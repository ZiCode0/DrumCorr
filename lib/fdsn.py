from obspy.clients.fdsn import Client

fdsn_client = None


def init_client(url):
    global fdsn_client
    fdsn_client = Client(url)


def get_inventory(network: str, station: str, location: str,
                  channel: str, level='response', start_time=None, end_time=None, plot=False):
    # client = Client()

    if location == '':
        location = None

    inventory = fdsn_client.get_stations(
        network=network,
        station=station,
        location=location,
        channel=channel,
        level=level,
        starttime=start_time,
        endtime=end_time
    )
    # plot results
    if plot:
        for channel in inventory[0][0]:
            channel.response.plot(min_freq=0.01, sampling_rate=200)

    return inventory

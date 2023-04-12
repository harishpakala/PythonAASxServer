

def function(pyAAS, *args):
    """Updates all channels referenced by its name in *args"""
    for channel_name in args:
        pyAAS.channels[channel_name].update()

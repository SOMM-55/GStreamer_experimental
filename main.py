import sys
import json
import random
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, GLib



Gst.init(sys.argv)


Gst.debug_set_active(True)
Gst.debug_set_default_threshold(5)

def on_debug(category, level, dfile, dfctn, dline, source, message, user_data):
    if source:
        print('\n\n\n\n Debug {} {}: {}'.format(
            Gst.DebugLevel.get_name(level), source.name, message.get()))
    else:
       pass
       # print('Debug {}: {}'.format(
       #     Gst.DebugLevel.get_name(level), message.get()))


Gst.debug_add_log_function(on_debug, None)




loop = GLib.MainLoop()

with open('stream_info.json', 'r') as sti:
        stream_info = json.load(sti)

input_file = stream_info["input_file_loc"][random.randint(0, len(stream_info["input_file_loc"]) -1)]
input_stream_url = stream_info["input_stream_ulr"][random.randint(0,len(stream_info["input_stream_ulr"]) - 1)]
output_stream_url = stream_info["output_stream_url"][random.randint(0,len(stream_info["output_stream_url"]) - 1)]
output_stream_key = stream_info["output_stream_key"]




MODE = "local"
if len( sys.argv ) > 1:
        MODE = sys.argv[1]

if MODE == "local":
        pipeline = Gst.parse_launch(f"filesrc location={input_file} ! qtdemux name=demux flvmux name=mux streamable=true demux.video_0 ! queue ! mux.video demux.audio_0 ! queue ! mux.audio mux.src ! rtmpsink location={output_stream_url + output_stream_key}")
else:
        pipeline = Gst.parse_launch(f"rtmpsrc location={input_stream_url} ! flvdemux name=demux flvmux name=mux streamable=true demux.video ! queue ! mux.video demux.audio ! queue ! mux.audio mux.src ! rtmpsink location={output_stream_url + output_stream_key}")


pipeline.set_state(Gst.State.PLAYING)
bus = pipeline.get_bus()
bus.add_signal_watch()
bus.enable_sync_message_emission()

def on_message(bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop()):
    mtype = message.type
    """
        Gstreamer Message Types and how to parse
  https://lazka.github.io/pgi-docs/Gst-1.0/flags.html#Gst.MessageType
    """
    if mtype == Gst.MessageType.EOS:
        # Handle End of Stream
        print("End of stream")
        loop.quit()
    elif mtype == Gst.MessageType.ERROR:
        # Handle Errors
        err, debug = message.parse_error()
        print(err, debug)
        loop.quit()
    elif mtype == Gst.MessageType.WARNING:
        # Handle warnings
        err, debug = message.parse_warning()
        print(err, debug)
    elif mtype == Gst.MessageType.BUFFERING:
        print("Bus call: Buffering\n")
    elif mtype == Gst.MessageType.STATE_CHANGED:
        old_state, new_state, pending_state = message.parse_state_changed()
        print((
            f"Bus call: Pipeline state changed from {old_state.value_nick} to {new_state.value_nick} "
            f"(pending {pending_state.value_nick})"
        ))
    elif mtype == Gst.MessageType.STREAM_STATUS:
        type, som = message.parse_stream_status()
        print(f"Stream Staus: {type} --- {som}")
    else:
        print(mtype,"********", message)
    return True

# bus.connect("message", on_message, None)

try:
    loop.run()
except:
    loop.quit()

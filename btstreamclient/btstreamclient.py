#!/usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (C) 2012 Gabriel Mendonça
#
# This file is part of BTStream.
# BTStream is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BTStream is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BTStream.  If not, see <http://www.gnu.org/licenses/>.
#
#
# BTStream.h
#
#  Created on: 23/01/2012
#      Author: gabriel
#

import sys

import pygst
pygst.require("0.10")
import gst
import gtk

class Main:
    def __init__(self, args):
        if len(args) != 1:
            print "Usage: python btstreamclient.py torrent_path"
            sys.exit()

        self.args = args

        self.pipeline = self.create_pipeline()

        self.configure_message_handling()

        # Starting playback
        self.pipeline.set_state(gst.STATE_PLAYING)

    def create_pipeline(self):
        pipeline =  gst.Pipeline("video-player-pipeline")

        # Creating elements
        self.src = gst.element_factory_make("btstreamsrc", "src")
        self.decoder = gst.element_factory_make("decodebin2", "decoder")
        self.audio_sink = self.create_audio_sink()
        self.video_sink = self.create_video_sink()

        # Configuring elements
        self.src.set_property("torrent", self.args[0])

        # Configuring callbacks
        self.decoder.connect("new-decoded-pad", self.handle_decoded_pad)

        # Adding elements
        pipeline.add(self.src, self.decoder, self.audio_sink, self.video_sink)

        # Linking elements
        gst.element_link_many(self.src, self.decoder)

        return pipeline

    def handle_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            gtk.main_quit()

        elif t == gst.MESSAGE_ERROR:
            self.pipeline.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            print "Error: %s" % err
            print debug
            gtk.main_quit()

    def create_audio_sink(self, fake=False):
        if fake:
            return gst.element_factory_make("fakesink", "audio-sink")
        
        audio_sink_bin = gst.Bin("audio-sink")

        # Creating elements
        queue = gst.element_factory_make("queue", "audio-queue")
        converter = gst.element_factory_make("audioconvert", "audio-converter")
        resampler = gst.element_factory_make("audioresample", "audio-resampler")
        sink = gst.element_factory_make("autoaudiosink", "audio-sink")

        # Adding elements
        audio_sink_bin.add(queue, converter, resampler, sink)

        # Linking elements
        gst.element_link_many(queue, converter, resampler, sink)

        # Adding ghost pad
        sink_pad = gst.GhostPad("sink", queue.get_pad("sink"))
        audio_sink_bin.add_pad(sink_pad)

        return audio_sink_bin

    def create_video_sink(self, fake=False):
        if fake:
            return gst.element_factory_make("fakesink", "video-sink")

        video_sink_bin = gst.Bin("video-sink")

        # Creating elements
        queue = gst.element_factory_make("queue", "video-queue")
        converter = gst.element_factory_make("ffmpegcolorspace", "video-converter")
        sink = gst.element_factory_make("autovideosink", "video-sink")

        # Adding elements
        video_sink_bin.add(queue, converter, sink)

        # Linking elements
        gst.element_link_many(queue, converter, sink)

        # Adding ghost pad
        sink_pad = gst.GhostPad("sink", queue.get_pad("sink"))
        video_sink_bin.add_pad(sink_pad)

        return video_sink_bin

    def handle_decoded_pad(self, demuxer, new_pad, is_last):
        structure_name = new_pad.get_caps()[0].get_name()
        if structure_name.startswith("audio"):
            new_pad.link(self.audio_sink.get_pad("sink"))

        elif structure_name.startswith("video"):
            new_pad.link(self.video_sink.get_pad("sink"))

    def configure_message_handling(self):
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.handle_message)



if __name__ == "__main__":
    start=Main(sys.argv[1:])
    gtk.main()

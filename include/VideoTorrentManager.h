/*
 * Copyright 2011 Gabriel Mendonça
 *
 * This file is part of BiVoD.
 * BiVoD is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * BiVoD is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with BiVoD.  If not, see <http://www.gnu.org/licenses/>.
 *
 *
 * VideoTorrentManager.h
 *
 *  Created on: 06/09/2011
 *      Author: gabriel
 */

#ifndef VIDEOTORRENTMANAGER_H_
#define VIDEOTORRENTMANAGER_H_

#include <libtorrent/session.hpp>

#include "VideoPlayer.h"

using namespace libtorrent;

namespace bivod {

/**
 * Manages video torrents through libtorrent.
 * Sends downloaded pieces to a VideoPlayer in order to be played.
 */
class VideoTorrentManager {
public:
	VideoTorrentManager(VideoPlayer* video_player);

	/**
	 * Starts the download of specified torrent.
	 * The feeding thread will be started.
	 */
	void add_torrent(std::string file_name, std::string save_path);

	/**
	 * Sends downloaded pieces to VideoPlayer.
	 * Pieces will be get through a libtorrent alert.
	 */
	void feed_video_player();

private:
	session m_session;
    torrent_handle m_torrent_handle;
	VideoPlayer* m_video_player;
    int m_pieces_to_play;
};

} /* namespace bivod */

#endif /* VIDEOTORRENTMANAGER_H_ */
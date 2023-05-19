
ML_HELP = """
<code>/cmd</code> link n: newname pswd: xx(zip/unzip)

<b>By replying to link/file:</b>
<code>/cmd</code> n: newname pswd: xx(zip/unzip)

<b>Direct link authorization:</b>
<code>/cmd</code> link n: newname pswd: xx(zip/unzip)
<b>username</b>
<b>password</b>

<b>Bittorrent seed</b>:
<code>/cmd</code> <b>d</b> link or by replying to file/link
To specify ratio and seed time add d:ratio:time. Ex: d:0.7:10 (ratio and time) or d:0.7 (only ratio) or d::10 (only time) where time in minutes.
Those options should be always before n: or pswd:

<b>Multi links only by replying to first link/file:</b>
<code>/cmd</code> 10(number of links/files)
Number should be always before n: or pswd:

<b>Multi links within same upload directory only by replying to first link/file:</b>
<code>/cmd</code> 10(number of links/files) m:folder_name
Number and m:folder_name (folder_name without space) should be always before n: or pswd:

<b>TG Links</b>:
Treat links like any direct link
Some links need user access.
Three types of links:
Public: <code>https://t.me/channel_name/message_id</code>
Private: <code>tg://openmessage?user_id=xxxxxx&message_id=xxxxx</code>
Super: <code>https://t.me/c/channel_id/message_id</code>

<b>Upload</b>:
<code>/cmd</code> link up: <code>rcl</code> (To select rclone config, remote and path)
You can directly add the upload path. up: remote:dir/subdir
If you want to add path manually from your config (uploaded from usetting) add <code>mrcc:</code> before the path without space
<code>/cmd</code> link up: <code>mrcc:</code>main:dump

<b>Rclone Flags</b>:
<code>/cmd</code> link|path|rcl up: path|rcl rcf: --buffer-size:8M|--drive-starred-only|key|key:value
This will override all other flags except --exclude
Check here all <a href='https://rclone.org/flags/'>RcloneFlags</a>.

<b>NOTES:</b>
1. When use cmd by reply don't add any option in link msg! Always add them after cmd msg!
2. Options (<b>n: and pswd:</b>) should be added randomly after the link if link along with the cmd and after any other option
3. Options (<b>d, m: and multi</b>) should be added randomly before the link and before any other option.
5. (n:) option doesn't work with torrents.
"""



YT_HELP = """
<b>Send link along with command line:</b>
<code>/cmd</code> s link n: newname pswd: xx(zip) opt: x:y|x1:y1

<b>By replying to link:</b>
<code>/cmd</code> n: newname pswd: xx(zip) opt: x:y|x1:y1

<b>Quality Buttons:</b>
Incase default quality added but you need to select quality for specific link or links with multi links feature.
<code>/cmd</code> s link
This option should be always before n:, pswd: and opt:

<b>Options Example:</b> opt: playliststart:^10|fragment_retries:^inf|matchtitle:S13|writesubtitles:true|live_from_start:true|postprocessor_args:{"ffmpeg": ["-threads", "4"]}|wait_for_video:(5, 100)

<b>Multi links only by replying to first link:</b>
<code>/cmd</code> 10(number of links)
Number should be always before n:, pswd: and opt:

<b>Multi links within same upload directory only by replying to first link:</b>
<code>/cmd</code> 10(number of links) m:folder_name
Number and m:folder_name should be always before n:, pswd: and opt:

<b>Options Note:</b> Add `^` before integer or float, some values must be numeric and some string.
Like playlist_items:10 works with string, so no need to add `^` before the number but playlistend works only with integer so you must add `^` before the number like example above.
You can add tuple and dict also. Use double quotes inside dict.

<b>Upload</b>:
<code>/cmd</code> link up: <code>rcl</code> (To select rclone config, remote and path)
You can directly add the upload path. up: remote:dir/subdir
If you want to add path manually from your config (uploaded from usetting) add <code>mrcc:</code> before the path without space
<code>/cmd</code> link up: <code>mrcc:</code>main:dump

<b>Rclone Flags</b>:
<code>/cmd</code> link up: path|rcl rcf: --buffer-size:8M|--drive-starred-only|key|key:value
This will override all other flags except --exclude
Check here all <a href='https://rclone.org/flags/'>RcloneFlags</a>.

<b>NOTES:</b>
1. When use cmd by reply don't add any option in link msg! Always add them after cmd msg!
2. Options (<b>s, m: and multi</b>) should be added randomly before link and before any other option.
3. Options (<b>n:, pswd: and opt:</b>) should be added randomly after the link if link along with the cmd or after cmd if by reply.
4. You can always add video quality from yt-dlp api options.
5. Don't add file extension while rename using `n:`

Check all yt-dlp api options from this <a href='https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/YoutubeDL.py#L184'>FILE</a> or use this <a href='https://t.me/mltb_official/177'>script</a> to convert cli arguments to api options.
"""
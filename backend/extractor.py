import os
import local_runtime
from urllib.parse import urlsplit, urlunsplit
import yt_dlp
import time
import random
from apify_client import ApifyClient

# Apify API Configuration
# Key resolved only at the provider boundary.
APIFY_ACTOR_ID = local_runtime.setting("VPS_APIFY_ACTOR_ID", "faVsWy9VTSNVIhWpR")  # YouTube Transcript Extractor

def clean_url(url):
    """
    Forces the URL to point to the 'Popular' tab so we get
    Viral Hits (Views), not just Recent uploads.
    """
    parsed = urlsplit(url)
    path = parsed.path.rstrip('/')
    if not path.endswith('/videos'):
        path += '/videos'
    return urlunsplit((parsed.scheme, parsed.netloc, path, 'view=0&sort=p', ''))

def get_viral_videos(channel_url, limit, progress_callback=None):
    local_runtime.require_external()
    target_url = clean_url(channel_url)

    if progress_callback:
        progress_callback({
            'status': 'scanning',
            'message': f'🎯 Targeted URL: {target_url}',
            'progress': 5
        })

    ydl_opts = {
        'extract_flat': True,
        'playlistend': limit,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            if 'entries' in info:
                return list(info['entries'])
    except Exception as e:
        if progress_callback:
            progress_callback({
                'status': 'error',
                'message': 'Video discovery failed.',
                'progress': 0
            })
        return []

def get_transcript_apify(video_id, progress_callback=None):
    """
    Get transcript using Apify API for provider-managed transcript extraction
    Uses actor: faVsWy9VTSNVIhWpR (YouTube Transcript Extractor)
    """
    local_runtime.require_external()

    try:
        # Initialize Apify client
        client = ApifyClient(local_runtime.provider_key('apify'))

        # Prepare the Actor input - this actor expects videoUrl (singular)
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        run_input = {
            "videoUrl": video_url
        }

        # Run the Actor and wait for it to finish
        run = client.actor(APIFY_ACTOR_ID).call(run_input=run_input)

        # Fetch results from the run's dataset
        transcript_text = ""
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():

            # The actor returns {"data": [{"start": "...", "dur": "...", "text": "..."}, ...]}
            if 'data' in item and isinstance(item['data'], list):
                # Extract text from each segment and join
                segments = [seg.get('text', '') for seg in item['data'] if seg.get('text')]
                transcript_text = " ".join(segments)

        if transcript_text:
            return transcript_text
        else:
            return None

    except Exception as e:
        print('Apify extraction failed; provider details omitted.')
        return None

def extract_viral_content(channel_url, limit=20, progress_callback=None):
    """
    Main extraction function that can report progress
    Uses Apify for transcript extraction
    """
    if progress_callback:
        progress_callback({
            'status': 'starting',
            'message': '🚀 Initializing Viral Extractor...',
            'progress': 0
        })

    videos = get_viral_videos(channel_url, limit, progress_callback)

    if not videos:
        if progress_callback:
            progress_callback({
                'status': 'error',
                'message': '❌ No videos found. Check URL.',
                'progress': 0
            })
        return None

    full_data = "=== VIRAL DNA ANALYSIS ===\n(Sorted by Most Popular of All Time)\n\n"
    count = 0
    total = len(videos)

    if progress_callback:
        progress_callback({
            'status': 'extracting',
            'message': f'✅ Found {total} Viral Hits. Extracting transcripts via Apify...',
            'progress': 10
        })

    for idx, v in enumerate(videos):
        title = v.get('title', 'Unknown')
        v_id = v.get('id')

        # Calculate progress (10% to 90% during extraction)
        current_progress = 10 + int((idx / total) * 80)

        if progress_callback:
            progress_callback({
                'status': 'extracting',
                'message': f'[{idx+1}/{total}] Extracting via Apify: {title[:50]}...',
                'progress': current_progress,
                'current': idx + 1,
                'total': total
            })

        text = get_transcript_apify(v_id, progress_callback)

        if text:
            full_data += f"### VIDEO: {title} ###\nURL: https://youtu.be/{v_id}\n\n{text}\n\n"
            count += 1
            if progress_callback:
                progress_callback({
                    'status': 'success',
                    'message': f'✅ [{idx+1}/{total}] Successfully extracted: {title[:40]}',
                    'progress': current_progress
                })
        else:
            if progress_callback:
                progress_callback({
                    'status': 'warning',
                    'message': f'⚠️ No subtitles found for: {title[:40]}',
                    'progress': current_progress
                })

        # Small delay between Apify calls (Apify handles rate limiting internally)
        time.sleep(random.uniform(1, 2))

    if count == 0:
        if progress_callback:
            progress_callback({'status': 'error', 'message': 'No transcripts available.', 'progress': 0})
        return None

    # Save to file
    local_runtime.DATA_DIR.mkdir(exist_ok=True)
    output_file = local_runtime.DATA_DIR / 'viral_dna.txt'
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_data)

    if progress_callback:
        progress_callback({
            'status': 'complete',
            'message': f'Transcripts ready: {count} videos',
            'progress': 100,
            'output_file': output_file.name,
            'videos_processed': count
        })

    return {
        'success': True,
        'output_file': output_file.name,
        'videos_processed': count,
        'content': full_data
    }

"""Read public YouTube playback metadata; no audio, identity or grader access claim."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parent
VIDEOS={1:'tMAmXiDBVBg',2:'EZolrbd3xOQ',3:'sqgNrHPguZ4'}

def main():
    results=[]
    for number, video_id in VIDEOS.items():
        row={'video':number,'id':video_id,'url':'https://youtu.be/'+video_id,
             'duration_limit_seconds':180 if number==1 else 300}
        try:
            request=Request('https://www.youtube.com/watch?v='+video_id,
                            headers={'User-Agent':'Mozilla/5.0'})
            with urlopen(request,timeout=25) as response:
                page=response.read().decode('utf-8')
            match=re.search(r'ytInitialPlayerResponse\s*=\s*',page)
            if not match:raise ValueError('No player response in page; playback not verified')
            player,_=json.JSONDecoder().raw_decode(page[match.end():])
            details=player.get('videoDetails',{})
            row['playability_status']=player.get('playabilityStatus',{}).get('status')
            row['duration_seconds']=int(details['lengthSeconds']) if details.get('lengthSeconds') else None
            row['within_limit']=(row['duration_seconds']<=row['duration_limit_seconds']
                                 if row['duration_seconds'] is not None else None)
            row['is_private']=details.get('isPrivate')
            row['caption_track_count']=len(player.get('captions',{}).get('playerCaptionsTracklistRenderer',{}).get('captionTracks',[]))
            row['meaning']='Public page metadata only; actual media decoding, webcam and instructional-team access unverified.'
        except Exception as error:
            row['error']=str(error)
            row['meaning']='Metadata unavailable; this does not establish that the video is inaccessible.'
        results.append(row)
    output={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'videos':results}
    (ROOT/'evidence/video-metadata.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
